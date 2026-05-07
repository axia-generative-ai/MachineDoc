from pydantic import BaseModel, ConfigDict
from datetime import datetime

class SearchManual(BaseModel):
    manual_id: int
    title: str
    category: str
    version: str
    saved_at: datetime

    model_config = ConfigDict(from_attributes=True)