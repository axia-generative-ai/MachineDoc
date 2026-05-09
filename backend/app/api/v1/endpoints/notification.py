from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api import deps
from app.crud.crud_notification import notification_repository
from app.models.notification import ReadStatus
from app.models.user import User
from app.schemas.notification import NotificationResponse

router = APIRouter()


class ReadStatusUpdate(BaseModel):
    is_read: ReadStatus


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


@router.patch(
    "/{notification_id}",
    summary="알림 상태 변경",
    response_model=NotificationResponse,
)
def update_notification(
    notification_id: int,
    body: ReadStatusUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    알림의 is_read 상태를 변경합니다 (`미확인` / `확인` / `완료`).
    """
    updated = notification_repository.update_read_status(db, notification_id, body.is_read)
    if not updated:
        raise HTTPException(status_code=404, detail="해당 알림을 찾을 수 없습니다.")
    # response_model에 equipment 정보 포함되어 있어 다시 조회
    rows = notification_repository.list_with_equipment(db, limit=500)
    target = next((r for r in rows if r["notification_id"] == notification_id), None)
    if not target:
        raise HTTPException(status_code=404, detail="조회 실패")
    return target
