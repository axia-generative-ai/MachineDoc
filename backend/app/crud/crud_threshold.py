from typing import Optional
from sqlalchemy.orm import Session
from app.models.threshold import EquipmentThreshold
from app.models.log import DataType
from app.schemas.threshold import ThresholdResponse

class CRUDThreshold:
    def get_by_equipment_and_type(
        self, db: Session, *, equipment_id: int, data_type: DataType
    ) -> Optional[ThresholdResponse]:
        db_obj = db.query(EquipmentThreshold).filter(
            EquipmentThreshold.equipment_id == equipment_id,
            EquipmentThreshold.data_type == data_type
        ).first()
        
        if db_obj:
            # from_orm (V2: from_attributes) 설정 덕분에 바로 변환 가능
            return ThresholdResponse.model_validate(db_obj)
        return None

threshold_repository = CRUDThreshold()