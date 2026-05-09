from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.notification import Notification, ReadStatus
from app.models.log import EquipmentLog
from app.models.equipment import Equipment
from app.schemas.notification import NotificationCreate


class CRUDNotification:
    def create(self, db: Session, *, obj_in: NotificationCreate) -> Notification:
        db_obj = Notification(**obj_in.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_unread_count(self, db: Session) -> int:
        return db.query(Notification).filter(Notification.is_read == ReadStatus.UNREAD).count()

    def list_with_equipment(self, db: Session, *, limit: int = 100) -> List[dict]:
        """notification × log × equipment join + 장비별 매핑된 첫 오류코드 추천."""
        from app.models.error_code import ErrorCode
        from app.models.saved_manual import SavedManual
        rows = (
            db.query(
                Notification.notification_id,
                Notification.log_id,
                Notification.message,
                Notification.is_read,
                Notification.level,
                Notification.occurred_at,
                EquipmentLog.equipment_id,
                Equipment.equipment_code,
                Equipment.location,
            )
            .join(EquipmentLog, EquipmentLog.log_id == Notification.log_id)
            .join(Equipment, Equipment.equipment_id == EquipmentLog.equipment_id)
            .order_by(Notification.notification_id.desc())
            .limit(limit)
            .all()
        )

        # equipment_id별 매핑된 첫 코드 캐시 (한 번만 쿼리)
        eq_to_code: dict[int, str] = {}
        if rows:
            eq_ids = list({row.equipment_id for row in rows})
            mapping_rows = (
                db.query(SavedManual.equipment_id, ErrorCode.code_name)
                .join(ErrorCode, ErrorCode.manual_id == SavedManual.manual_id)
                .filter(SavedManual.equipment_id.in_(eq_ids))
                .order_by(SavedManual.equipment_id, ErrorCode.error_code_id.asc())
                .all()
            )
            for eq_id, code in mapping_rows:
                if eq_id not in eq_to_code:
                    eq_to_code[eq_id] = code

        result = []
        for row in rows:
            d = dict(row._mapping)
            d["suggested_error_code"] = eq_to_code.get(row.equipment_id)
            result.append(d)
        return result

    def update_read_status(self, db: Session, notification_id: int, is_read: ReadStatus) -> Optional[Notification]:
        db_obj = db.query(Notification).filter(Notification.notification_id == notification_id).first()
        if db_obj:
            db_obj.is_read = is_read
            db.commit()
            db.refresh(db_obj)
        return db_obj


notification_repository = CRUDNotification()