from sqlalchemy.orm import Session, joinedload
from sqlalchemy import asc
from app.models.notification import Notification, ReadStatus, NotificationLevel
from app.models.log import EquipmentLog
from app.models.equipment import Equipment
from app.schemas.notification import NotificationCreate
from typing import Optional

from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.notification import Notification, ReadStatus
from app.models.log import EquipmentLog
from app.models.equipment import Equipment
from app.models.error_code import ErrorCode
from app.models.saved_manual import SavedManual
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

    def get_by_id(self, db: Session, id: int):
        return db.query(Notification).filter(Notification.notification_id == id).first()

    def update_is_read_field(self, db: Session, *, db_obj: Notification, new_status: ReadStatus):
        # 모델 필드명인 is_read에 Enum 값을 직접 할당
        db_obj.is_read = new_status
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get_multi_with_filter(
        self, 
        db: Session, 
        *, 
        skip: int, 
        limit: int,
        is_read: ReadStatus = None,
        noti_level: NotificationLevel = None,
        equipment_code: str = None
    ):
        # 1. 조인 경로 설정: Notification -> Log -> Equipment
        # 조인 순서가 중요합니다.
        query = db.query(Notification)\
            .join(EquipmentLog, Notification.log_id == EquipmentLog.log_id)\
            .join(Equipment, EquipmentLog.equipment_id == Equipment.equipment_id)

        # 2. 동적 필터링 적용
        if is_read:
            query = query.filter(Notification.is_read == is_read)
        if noti_level:
            query = query.filter(Notification.noti_level == noti_level)
        if equipment_code:
            query = query.filter(Equipment.equipment_code == equipment_code)

        # 3. 전체 개수 계산 (필터링된 결과 기준)
        total_count = query.count()

        # 4. 정렬 및 페이지네이션 (최신순)
        # 💡 성능 팁: 데이터를 가져올 때 관계된 객체를 미리 로드(Eager Loading)하면 N+1 문제를 방지할 수 있습니다.
        results = query.options(joinedload(Notification.log).joinedload(EquipmentLog.equipment))\
                       .order_by(asc(Notification.occurred_at))\
                       .offset(skip)\
                       .limit(limit)\
                       .all()

        return results, total_count

    def get_with_details(self, db: Session, notification_id: int):
            return db.query(Notification)\
                .options(
                    joinedload(Notification.log)
                    .joinedload(EquipmentLog.equipment)
                )\
                .filter(Notification.notification_id == notification_id)\
                .first()

notification_repository = CRUDNotification()