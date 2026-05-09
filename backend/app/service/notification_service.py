from sqlalchemy.orm import Session
from app.crud.crud_notification import notification_repository
from app.crud.crud_equipment import equipment_repository
from app.models.error_code import ErrorCode
from app.schemas.notification import NotificationCreate, NotificationResponse
from app.models.log import EquipmentLog, LogStatus
from app.models.equipment import Equipment, EquipmentStatus
from app.models.notification import ReadStatus, NotificationLevel
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

        # 2. Notification DB 저장
        new_noti = notification_repository.create(
            db, 
            obj_in=NotificationCreate(
                log_id=log.log_id,
                message=alert_message,
                is_read=ReadStatus.UNREAD,
                level=noti_level
            )
        )

        # 3. 설비 상태 업데이트 로직
        # 로그 상태가 ERROR인 경우 설비의 가동 상태도 ERROR로 전환
        if str(log.status) == str(LogStatus.ERROR) or log.status == LogStatus.ERROR:
            equipment_repository.update_status(
                db, 
                equipment_id=log.equipment_id, 
                status=EquipmentStatus.ERROR
            )

        # 5. 응답 스키마 조립 (DB 객체 + 추가 정보)
        # 해당 장비에 매핑된 첫 오류코드 (없으면 글로벌 fallback)
        from app.models.saved_manual import SavedManual
        suggested_code = (
            db.query(ErrorCode.code_name)
            .join(SavedManual, SavedManual.manual_id == ErrorCode.manual_id)
            .filter(SavedManual.equipment_id == equipment.equipment_id)
            .order_by(ErrorCode.error_code_id.asc())
            .limit(1)
            .scalar()
        )
        if not suggested_code:
            suggested_code = (
                db.query(ErrorCode.code_name).order_by(ErrorCode.error_code_id.asc()).limit(1).scalar()
            )
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
        }
        final_response = NotificationResponse(**response_data)

        # 4. 웹소켓 실시간 브로드캐스트
        # 프론트엔드에서 즉시 팝업이나 토스트 메시지를 띄울 수 있도록 데이터 전송
        await manager.broadcast({
            "event": "ANOMALY_DETECTED",
            "data": final_response.model_dump(mode='json')
        })
        
        return new_noti

notification_service = NotificationService()