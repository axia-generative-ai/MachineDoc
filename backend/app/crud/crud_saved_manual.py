from sqlalchemy.orm import Session
from app.models.saved_manual import SavedManual
from app.schemas.manual import ManualCreateInternal

class ManualRepository:
    def get_manuals_by_category(self, db: Session, category: str):
        return db.query(SavedManual).filter(SavedManual.category == category).all()

    def get_manual_by_id(self, db: Session, manual_id: int):
        return db.query(SavedManual).filter(SavedManual.manual_id == manual_id).first()

    def create(self, db: Session, manual_internal: ManualCreateInternal) -> SavedManual:
        db_manual = SavedManual(**manual_internal.model_dump())
        db.add(db_manual)
        db.flush()
        return db_manual

manual_repository = ManualRepository()