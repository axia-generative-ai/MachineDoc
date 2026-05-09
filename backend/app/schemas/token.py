from pydantic import BaseModel
from datetime import datetime

class RefreshTokenCreate(BaseModel):
    user_id: int
    token: str
    expires_at: datetime

class RefreshToken(RefreshTokenCreate):
    token_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class TokenRefreshRequest(BaseModel):
    refresh_token: str