from typing import Optional
from sqlalchemy.orm import Session

from app.models.action_log import ActionLog
from app.models.search_history import SearchHistory
from app.schemas.action_log import ActionLogCreate


class ActionLogRepository:
    def get_by_history(self, db: Session, *, history_id: int) -> Optional[ActionLog]:
        return db.query(ActionLog).filter(ActionLog.history_id == history_id).first()

    def upsert_by_history(
        self,
        db: Session,
        *,
        history_id: int,
        obj_in: ActionLogCreate,
    ) -> ActionLog:
        existing = self.get_by_history(db, history_id=history_id)
        if existing:
            existing.action_sta = obj_in.action_sta
            existing.comment = obj_in.comment
            existing.duration = obj_in.duration
            db.add(existing)
            db.commit()
            db.refresh(existing)
            return existing
        new_obj = ActionLog(
            history_id=history_id,
            action_sta=obj_in.action_sta,
            comment=obj_in.comment,
            duration=obj_in.duration,
        )
        db.add(new_obj)
        db.commit()
        db.refresh(new_obj)
        return new_obj

    def list_by_user(self, db: Session, *, user_id: int, limit: int = 50):
        """ActionLog × SearchHistory join — 사용자 본인 조치 이력 + 원본 검색 정보."""
        rows = (
            db.query(
                ActionLog.action_log_id,
                ActionLog.history_id,
                ActionLog.action_sta,
                ActionLog.comment,
                ActionLog.duration,
                ActionLog.created_at,
                SearchHistory.query,
                SearchHistory.status.label("search_status"),
                SearchHistory.created_at.label("search_created_at"),
            )
            .join(SearchHistory, SearchHistory.history_id == ActionLog.history_id)
            .filter(SearchHistory.user_id == user_id)
            .order_by(ActionLog.action_log_id.desc())
            .limit(limit)
            .all()
        )
        return [dict(row._mapping) for row in rows]


action_log_repository = ActionLogRepository()
