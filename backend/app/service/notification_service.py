import random
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.crud.crud_notification import notification_repository
from app.crud.crud_equipment import equipment_repository
from app.schemas.notification import NotificationCreate, NotificationResponse, InfoNotificationResponse, NotificationDetailResponse
from app.schemas.log import InfoLogResponse
from app.schemas.equipment import InfoEquipmentResponse
from app.models.log import EquipmentLog, LogStatus
from app.models.equipment import Equipment, EquipmentStatus
from app.models.notification import ReadStatus, NotificationLevel
from app.models.error_code import ErrorCode
from app.core.websocket import manager

class NotificationService:
    async def process_anomaly_notification(self, db: Session, log: EquipmentLog, equipment: Equipment):
        # 1. 알림 메시지 구성
        alert_message = f"[{log.data_type.value}] 이상 수치 감지: {log.value} (상태: {log.status.value})"
        
        if log.status == LogStatus.ERROR:
            noti_level = NotificationLevel.URGENT    # "긴급"
        elif log.status == LogStatus.WARNING:
            noti_level = NotificationLevel.WARNING   # "경고"
        else:
            noti_level = NotificationLevel.CAUTION   # "주의" (그 외 상황)

        # 2. 추천 오류코드 결정 (anomaly_rules.json 풀에서 random.choice).
        # INSERT 전에 미리 결정해서 notification.suggested_error_code 컬럼에 박제.
        # → REST seed 새로고침해도 동일한 코드가 보임.
        suggested_code = _pick_suggested_code(
            db,
            equipment_code=equipment.equipment_code,
            equipment_id=equipment.equipment_id,
            data_type=log.data_type.value,
        )

        # 3. Notification DB 저장 (suggested_error_code 함께 저장)
        new_noti = notification_repository.create(
            db,
            obj_in=NotificationCreate(
                log_id=log.log_id,
                message=alert_message,
                is_read=ReadStatus.UNREAD,
                level=noti_level,
                suggested_error_code=suggested_code,
            )
        )

        # 4. 설비 상태 업데이트 로직
        # 로그 상태가 ERROR인 경우 설비의 가동 상태도 ERROR로 전환
        if str(log.status) == str(LogStatus.ERROR) or log.status == LogStatus.ERROR:
            equipment_repository.update_status(
                db,
                equipment_id=log.equipment_id,
                status=EquipmentStatus.ERROR
            )

        # 5. 응답 스키마 조립
        response_data = {
            "notification_id": new_noti.notification_id,
            "log_id": new_noti.log_id,
            "message": new_noti.message,
            "is_read": new_noti.is_read,
            "level": new_noti.level,
            "occurred_at": new_noti.occurred_at,
            "equipment_id": equipment.equipment_id,
            "equipment_code": equipment.equipment_code,
            "location": equipment.location,
            "suggested_error_code": suggested_code,
            "suggested_error_codes": [suggested_code] if suggested_code else [],  # 하위호환
        }
        final_response = NotificationResponse(**response_data)

        # 4. 웹소켓 실시간 브로드캐스트
        # 프론트엔드에서 즉시 팝업이나 토스트 메시지를 띄울 수 있도록 데이터 전송
        await manager.broadcast({
            "event": "ANOMALY_DETECTED",
            "data": final_response.model_dump(mode='json')
        })
        
        return new_noti

    def update_status(self, db: Session, notification_id: int, new_status: ReadStatus):
        # 1. 알림 존재 여부 및 소유권 확인
        notification = notification_repository.get_by_id(db, id=notification_id)
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="알림을 찾을 수 없습니다."
            )

        # 2. 상태 업데이트 로직 (필드명 is_read에 Enum 값 할당)
        return notification_repository.update_is_read_field(
            db, 
            db_obj=notification, 
            new_status=new_status
        )
    
    def get_notifications_list(
        self, 
        db: Session, 
        skip: int, 
        limit: int, 
        is_read: ReadStatus = None, 
        noti_level: NotificationLevel = None, 
        equipment_code: str = None
    ):
        # 1. 리포지토리 호출 (results: Notification 객체 리스트)
        notifications, total = notification_repository.get_multi_with_filter(
            db,
            skip=skip,
            limit=limit,
            is_read=is_read,
            noti_level=noti_level,
            equipment_code=equipment_code
        )

        # 2. 데이터 평면화 (Flattening)
        # 프론트엔드에서 n.log.equipment.equipment_code 처럼 깊게 들어가지 않게 가공합니다.
        formatted_items = []
        for n in notifications:
            # 안전하게 데이터를 가져오기 위해 getattr이나 None 체크를 활용합니다.
            eq_code = None
            if n.log and n.log.equipment:
                eq_code = n.log.equipment.equipment_code

            item = {
                "notification_id": n.notification_id,
                "level": n.level,
                "message": n.message,
                "is_read": n.is_read,         # Enum 값이 반환됨 (미확인/확인/완료)
                "occurred_at": n.occurred_at,
                "equipment_code": eq_code,    # 조인된 데이터에서 추출
                "log_id": n.log_id
            }
            formatted_items.append(item)

        return {
            "items": formatted_items,
            "total": total,
            "page": (skip // limit) + 1,      # 현재 페이지 계산 (옵션)
            "size": limit
        }

    def get_notification_detail(self, db: Session, notification_id: int) -> NotificationDetailResponse:
        # 1. 모든 관계 데이터(Log, Equipment)가 조인된 엔티티 조회
        notification = notification_repository.get_with_details(db, notification_id=notification_id)
        
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="해당 알림을 찾을 수 없습니다."
            )

        # 2. 데이터 유효성 체크 (로그와 설비 정보가 있는지 확인)
        if not notification.log or not notification.log.equipment:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="알림과 연결된 로그 또는 설비 데이터가 존재하지 않습니다."
            )

        # 3. 각 파트별로 스키마 매핑 및 합체
        # Pydantic의 model_validate는 DB 객체를 스키마 형태에 맞춰 자동으로 변환해줍니다.
        return NotificationDetailResponse(
            notification=InfoNotificationResponse.model_validate(notification),
            log=InfoLogResponse.model_validate(notification.log),
            equipment=InfoEquipmentResponse.model_validate(notification.log.equipment)
        )

def _pick_suggested_code(
    db: Session,
    *,
    equipment_code: str,
    equipment_id: int,
    data_type: str,
) -> str | None:
    """이상 감지 시 표시할 추천 오류코드 1개 (랜덤 선택).

    풀: 설비에 매핑된 매뉴얼의 error_code 전체 (data_type 무관).
    매뉴얼이 없으면 글로벌 error_code 50건으로 fallback.
    `equipment_code`/`data_type`은 향후 룰 도입 시 시그니처 유지를 위해 받지만
    현재는 사용 안 함.
    """
    from app.models.saved_manual import SavedManual

    eq_rows = (
        db.query(ErrorCode.code_name)
        .join(SavedManual, SavedManual.manual_id == ErrorCode.manual_id)
        .filter(SavedManual.equipment_id == equipment_id)
        .all()
    )
    pool = [r.code_name for r in eq_rows]

    if not pool:
        global_rows = db.query(ErrorCode.code_name).limit(50).all()
        pool = [r.code_name for r in global_rows]

    if not pool:
        return None

    return random.choice(pool)


notification_service = NotificationService()