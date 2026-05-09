from typing import Optional
from sqlalchemy.orm import Session
from app.models.equipment import Equipment, EquipmentStatus

class CRUDEquipment:
    def get_by_name(self, db: Session, *, name: str) -> Optional[Equipment]:
        return db.query(Equipment).filter(Equipment.equipment_code == name).first()
    
    def update_status(self, db: Session, *, equipment_id: int, status: EquipmentStatus):
        equipment = db.query(Equipment).filter(Equipment.equipment_id == equipment_id).update(
            {Equipment.state: status}
        )
        db.commit()
        return equipment

equipment_repository = CRUDEquipment()