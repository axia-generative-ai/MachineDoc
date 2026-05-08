from pydantic import BaseModel, ConfigDict
from app.models.log import DataType

class ThresholdResponse(BaseModel):
    threshold_id: int
    equipment_id: int
    data_type: DataType
    warning_threshold: float
    error_threshold: float

    # SQLAlchemy 객체를 Pydantic으로 자동 변환하기 위한 설정
    model_config = ConfigDict(from_attributes=True)