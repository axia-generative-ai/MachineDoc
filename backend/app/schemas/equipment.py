from pydantic import BaseModel, ConfigDict, Field
from app.models.equipment import LocationType, EquipmentStatus

class InfoEquipmentResponse(BaseModel):
    equipment_id: int
    location: LocationType
    equipment_code: str
    state:EquipmentStatus
    
    model_config = ConfigDict(from_attributes=True)