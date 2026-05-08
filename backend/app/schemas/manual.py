from pydantic import BaseModel, ConfigDict
from datetime import datetime

class SearchManual(BaseModel):
    manual_id: int
    title: str
    category: str
    version: str
    saved_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ManualCreate(BaseModel):
    title: str
    category: str
    version: str

class ManualCreateInternal(ManualCreate):
    user_id: int
    file_url: str

# 업로드 성공 후 반환할 응답 스키마 (선택 사항)
class ManualResponse(BaseModel):
    manual_id: int
    title: str
    message: str = "매뉴얼이 성공적으로 업로드되었습니다."

    model_config = ConfigDict(from_attributes=True)