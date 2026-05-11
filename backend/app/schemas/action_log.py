from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.models.action_log import ActionStatus

class ActionLogCreate(BaseModel):
    """조치 결과 등록 요청 body."""
    action_sta: ActionStatus
    comment: Optional[str] = None
    duration: Optional[int] = None

class ActionLogRead(BaseModel):
    action_log_id: int
    history_id: int
    action_sta: ActionStatus
    comment: Optional[str] = None
    duration: Optional[int] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class ActionLogWithHistory(ActionLogRead):
    """조치 이력 + 그 조치가 어떤 검색에 대한 것인지 함께 노출."""
    query: str
    search_status: str
    search_created_at: Optional[datetime] = None