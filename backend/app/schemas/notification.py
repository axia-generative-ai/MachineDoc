from pydantic import BaseModel, ConfigDict
from datetime import datetime
from app.models.notification import ReadStatus, NotificationLevel
from app.schemas.log import InfoLogResponse
from app.schemas.equipment import InfoEquipmentResponse

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
    occurred_at: datetime
    equipment_id: int
    equipment_code: str
    location: str

    model_config = ConfigDict(from_attributes=True)

class InfoNotificationResponse(BaseModel):
    notification_id: int
    message: str
    is_read: ReadStatus
    level: NotificationLevel

    model_config = ConfigDict(from_attributes=True)

class NotificationDetailResponse(BaseModel):
    notification: InfoNotificationResponse
    log: InfoLogResponse
    equipment: InfoEquipmentResponse

class ReadStatusUpdate(BaseModel):
    is_read: ReadStatus