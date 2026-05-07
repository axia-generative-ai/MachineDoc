# app/crud/crud_manual.py
from sqlalchemy.orm import Session
from app.models.saved_manual import SavedManual

def get_manuals_by_category(db: Session, category: str):
    return db.query(SavedManual).filter(SavedManual.category == category).all()

def get_manual_by_id(db: Session, manual_id: int):
    return db.query(SavedManual).filter(SavedManual.manual_id == manual_id).first()