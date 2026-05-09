from typing import Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from app.models.notification import ReadStatus, NotificationLevel

# 생성용 스키마
class NotificationCreate(BaseModel):
    log_id: int
    message: str
    is_read: ReadStatus = ReadStatus.UNREAD
    level: NotificationLevel

# 응답용 스키마 (웹소켓이나 API 결과값으로 사용)
class NotificationResponse(BaseModel):
    notification_id: int
    log_id: int
    message: str
    is_read: ReadStatus
    level: NotificationLevel
    occured_at: datetime
    equipment_id: int
    equipment_code: str
    location: str
    suggested_error_code: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)