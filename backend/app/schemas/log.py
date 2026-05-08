import enum
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from app.models.log import DataType, LogStatus

# [Schema 1] DB에 저장하거나 생성할 때 사용하는 데이터 구조
class EquipmentLogCreate(BaseModel):
    equipment_id: int = Field(..., description="설비 고유 ID")
    data_type: DataType = Field(..., description="데이터 타입 (진동/온도)")
    value: float = Field(..., description="측정 값")
    status: LogStatus = Field(default=LogStatus.NORMAL, description="분석된 상태")
    
    # 가상 로그 생성 시 시점 조절을 위해 Optional로 둡니다.
    # 값을 안 넣으면 DB의 server_default(현재시간)가 작동합니다.
    occurred_at: Optional[datetime] = Field(default=None)

    model_config = ConfigDict(from_attributes=True)

# [Schema 2] (선택) 외부에서 가상 로그 생성을 요청할 때 쓰는 간단한 구조
# 예: "특정 설비의 로그를 하나 만들어줘"라고 요청할 때
class VirtualLogRequest(BaseModel):
    equipment_name: str = Field(..., examples=["Motor_01"])

class EquipmentLogResponse(BaseModel):
    log_id: int
    equipment_id: int
    data_type: DataType
    value: float
    status: LogStatus
    occurred_at: datetime

    # SQLAlchemy 모델 객체를 Pydantic 스키마로 변환하기 위한 설정
    # (FastAPI가 DB 객체를 이 스키마에 자동으로 매핑해줍니다)
    model_config = ConfigDict(from_attributes=True)