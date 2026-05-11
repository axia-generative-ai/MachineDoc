from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.models.notification import NotificationLevel

class StatCardData(BaseModel):
    todayErrorCount: int
    yesterdayErrorCount: int
    unhandledNotificationCount: int
    totalNotificationCount: int
    avgActionDurationMinutes: Optional[float]
    actionGoalMinutes: int = 5
    manualCount: int
    errorCodeCount: int

class HourlyPoint(BaseModel):
    hour: str
    count: int

class AnomalyDigest(BaseModel):
    notification_id: int
    title: str
    level: NotificationLevel
    meta: str
    occurred_at: datetime
    equipment_code: str

class DashboardSummary(BaseModel):
    stats: StatCardData
    hourly_trend: List[HourlyPoint]
    anomaly_digest: List[AnomalyDigest]