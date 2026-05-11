from pydantic import BaseModel
from typing import Optional

class AIQueryRequest(BaseModel):
    log_id: int
    equipment_code: str
    data_type: str
    value: float

class AIQueryResponse(BaseModel):
    answer: str
    status: str = "success"