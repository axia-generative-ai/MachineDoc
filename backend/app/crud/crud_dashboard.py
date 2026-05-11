from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from app.models.log import EquipmentLog
from app.models.action_log import ActionLog
from app.models.notification import Notification, ReadStatus
from app.models.equipment import Equipment
from app.models.saved_manual import SavedManual
from app.models.error_code import ErrorCode

class CRUDDashboard:
    def get_error_count(self, db: Session, start: datetime, end: datetime = None):
        query = db.query(func.count(EquipmentLog.log_id)).filter(EquipmentLog.status != "정상")
        query = query.filter(EquipmentLog.occurred_at >= start)
        if end:
            query = query.filter(EquipmentLog.occurred_at < end)
        return query.scalar() or 0

    def get_notification_counts(self, db: Session):
        unhandled = db.query(func.count(Notification.notification_id))\
                      .filter(Notification.is_read == ReadStatus.UNREAD).scalar() or 0
        total = db.query(func.count(Notification.notification_id)).scalar() or 0
        return unhandled, total

    def get_avg_action_duration(self, db: Session):
        return db.query(func.avg(ActionLog.duration))\
                 .filter(ActionLog.duration.is_not(None)).scalar()

    def get_resource_counts(self, db: Session):
        manuals = db.query(func.count(SavedManual.manual_id)).scalar() or 0
        errors = db.query(func.count(ErrorCode.error_code_id)).scalar() or 0
        return manuals, errors

    def get_hourly_trend_rows(self, db: Session, since: datetime):
        return (
            db.query(
                func.to_char(EquipmentLog.occurred_at, "HH24").label("hour"),
                func.count(EquipmentLog.log_id),
            )
            .filter(EquipmentLog.status != "정상", EquipmentLog.occurred_at >= since)
            .group_by("hour")
            .all()
        )

    def get_recent_anomalies(self, db: Session, limit: int = 5):
        return (
            db.query(
                Notification.notification_id,
                Notification.message,
                Notification.level,
                Notification.occurred_at,
                EquipmentLog.value,
                EquipmentLog.data_type,
                Equipment.equipment_code,
            )
            .join(EquipmentLog, EquipmentLog.log_id == Notification.log_id)
            .join(Equipment, Equipment.equipment_id == EquipmentLog.equipment_id)
            .filter(Notification.is_read == ReadStatus.UNREAD)
            .order_by(Notification.notification_id.desc())
            .limit(limit)
            .all()
        )

dashboard_repository = CRUDDashboard()