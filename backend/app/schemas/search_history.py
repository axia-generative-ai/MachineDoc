from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class SearchHistoryRead(BaseModel):
    history_id: int
    user_id: int
    query: str
    result_content: str
    status: str
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)