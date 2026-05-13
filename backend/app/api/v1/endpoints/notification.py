from typing import List
from fastapi import APIRouter, Depends, status, Query
from app.db.session import get_db
from sqlalchemy.orm import Session

from app.api import deps
from app.crud.crud_notification import notification_repository
from app.models.notification import ReadStatus, NotificationLevel
from app.models.user import User
from app.schemas.notification import NotificationResponse, ReadStatusUpdate
from app.schemas.notification import NotificationDetailResponse
from app.service.notification_service import notification_service


router = APIRouter()

@router.get(
    "",
    summary="알림 이력 조회",
    response_model=List[NotificationResponse],
)
def list_notifications(
    limit: int = Query(100, le=500),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    가상 로그·이상 감지로 발생한 알림 이력을 최신순으로 반환합니다.
    notification × log × equipment 조인 결과로 설비 코드/위치까지 함께 노출합니다.
    """
    return notification_repository.list_with_equipment(db, limit=limit)

@router.get(
    "/filter", 
    status_code=200,
    summary="알림 목록 조회 (필터 및 페이지네이션)",
    responses={
        200: {
            "description": "조회 성공",
            "content": {
                "application/json": {
                    "example": {
                        "items": [
                            {
                                "id": 1,
                                "level": "WARN",
                                "message": "온도 상승 감지",
                                "is_read": "확인",
                                "occurred_at": "2026-05-08T15:30:00",
                                "equipment_code": "TEMP-001"
                            }
                        ],
                        "total": 125,
                        "page": 1,
                        "size": 20
                    }
                }
            }
        }
    }
)
async def get_notifications(
    skip: int = 0,
    limit: int = 20,
    is_read: ReadStatus = None,
    noti_level: NotificationLevel = None,
    equipment_code: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    시스템의 전체 알림 목록을 최신순으로 조회합니다.
    
    - **Pagination**: **skip**과 **limit**을 사용하여 페이지 처리가 가능합니다.
    - **Filtering**: 
        - **is_read**: 알림 상태별 필터 (미확인/확인/완료)
        - **noti_level**: 알림 위험도별 필터 (긴급/경고/주의)
        - **equipment_code**: 특정 설비와 관련된 알림만 조회
    - **Response**: 각 알림 객체에는 해당 알림의 원인이 된 **equipment_code**가 포함되어 반환됩니다.
    """
    return notification_service.get_notifications_list(
        db, 
        skip=skip, 
        limit=limit, 
        is_read=is_read, 
        noti_level=noti_level, 
        equipment_code=equipment_code
    )

@router.patch(
    "/{notification_id}/status", 
    status_code=status.HTTP_200_OK,
    summary="알림 상태 업데이트",
    responses={
        200: {"description": "성공적으로 상태가 변경됨"},
        404: {"description": "존재하지 않는 알림 ID"},
    })
async def change_notification_status(
    notification_id: int,
    body: ReadStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    특정 알림의 처리 상태를 변경합니다.
    - **UNREAD (미확인)**: 초기 상태
    - **CHECKED (확인)**: 사용자가 알림을 클릭하여 내용을 확인한 상태
    - **COMPLETED (완료)**: 알림에 대한 후속 조치(설비 점검 등)가 마무리된 상태
    """
    # 서비스 레이어 호출
    return notification_service.update_status(
        db, 
        notification_id=notification_id, 
        new_status=body.is_read
    )

@router.get(
    "/{notification_id}", 
    response_model=NotificationDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="알림 상세 정보 통합 조회",
    responses={
        200: {
            "description": "성공적으로 데이터를 조회함",
            "content": {
                "application/json": {
                    "example": {
                        "notification": {
                            "notification_id": 1,
                            "message": "센서 데이터 이상 감지",
                            "is_read": "미확인",
                            "level": "ERROR"
                        },
                        "log": {
                            "log_id": 105,
                            "data_type": "TEMPERATURE",
                            "value": 98.2,
                            "status": "ABNORMAL",
                            "occurred_at": "2026-05-08T17:00:00"
                        },
                        "equipment": {
                            "equipment_id": 5,
                            "location": "MAIN_FACTORY_1",
                            "equipment_code": "EQP-TEMP-001",
                            "state": "WARNING"
                        }
                    }
                }
            }
        },
        404: {"description": "요청한 알림 ID를 찾을 수 없음"},
        422: {"description": "알림과 연결된 로그나 설비 정보가 유효하지 않음 (데이터 무결성 오류)"}
    }
)
async def get_notification_detail(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    특정 알림 ID를 바탕으로 **알림 + 로그 + 설비** 정보를 단일 객체로 병합하여 반환합니다.
    
    ### 반환되는 정보:
    1. **notification**: 알림 자체의 메시지, 읽음 상태(is_read), 중요도(level)
    2. **log**: 알림의 원인이 된 데이터 값(value), 데이터 타입, 발생 시각
    3. **equipment**: 해당 로그가 발생한 설비의 위치, 설비 코드, 현재 상태
    
    사용자가 알림 리스트에서 특정 항목을 클릭했을 때 상세 팝업이나 페이지를 구성하기 위한 용도로 사용됩니다.
    """
    return notification_service.get_notification_detail(
        db, 
        notification_id=notification_id
    )