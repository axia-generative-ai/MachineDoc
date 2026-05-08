from sqlalchemy.orm import Session
from app.models.notification import Notification
from app.schemas.notification import NotificationCreate
from typing import Optional

class CRUDNotification:
    def create(self, db: Session, *, obj_in: NotificationCreate) -> Notification:
        # 1. 스키마를 딕셔너리로 변환하여 모델 생성
        db_obj = Notification(**obj_in.model_dump())
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_unread_count(self, db: Session) -> int:
        """읽지 않은 알림 개수 조회"""
        return db.query(Notification).filter(Notification.is_read == False).count()

    def mark_as_read(self, db: Session, notification_id: int) -> Optional[Notification]:
        """특정 알림 읽음 처리"""
        db_obj = db.query(Notification).get(notification_id)
        if db_obj:
            db_obj.is_read = True
            db.commit()
            db.refresh(db_obj)
        return db_obj

notification_repository = CRUDNotification()