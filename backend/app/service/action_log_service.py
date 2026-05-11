from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.search_history import SearchHistory
from app.crud.crud_action_log import action_log_repository
from app.schemas.action_log import ActionLogCreate


class ActionLogService:
    def create_or_update(self, db: Session, *, user_id: int, history_id: int, obj_in: ActionLogCreate):
        history = db.query(SearchHistory).filter(SearchHistory.history_id == history_id).first()
        if not history:
            raise HTTPException(status_code=404, detail="해당 검색 이력을 찾을 수 없습니다.")
        if history.user_id != user_id:
            raise HTTPException(status_code=403, detail="다른 사용자의 검색 이력에는 조치를 입력할 수 없습니다.")
        return action_log_repository.upsert_by_history(db, history_id=history_id, obj_in=obj_in)

    def list_for_user(self, db: Session, *, user_id: int, limit: int = 50):
        return action_log_repository.list_by_user(db, user_id=user_id, limit=limit)

action_log_service = ActionLogService()
