"""대시보드 집계 라우트.

홈 화면(`/dashboard`)에서 한 번에 가져갈 모든 KPI를 단일 응답으로 묶는다.
- 통계 카드 4종 (오늘 오류 / 미처리 알림 / 평균 대응시간 / 등록 매뉴얼)
- 24시간 시간대별 오류 발생 건수
- 확인 필요 이상징후 Top N (level=긴급/경고 우선)
"""

from datetime import datetime, timedelta, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api import deps
from app.models.action_log import ActionLog
from app.models.equipment import Equipment
from app.models.error_code import ErrorCode
from app.models.log import EquipmentLog
from app.models.notification import Notification, NotificationLevel, ReadStatus
from app.models.saved_manual import SavedManual
from app.models.user import User

router = APIRouter()


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


def _today_window():
    now = datetime.now(timezone.utc)
    start_today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    start_yesterday = start_today - timedelta(days=1)
    return start_today, start_yesterday, now


@router.get(
    "/summary",
    summary="대시보드 집계 (통계카드 + 추이 + 이상징후)",
    response_model=DashboardSummary,
)
def get_dashboard_summary(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    start_today, start_yesterday, now = _today_window()

    today_errors = (
        db.query(func.count(EquipmentLog.log_id))
        .filter(EquipmentLog.status != "정상", EquipmentLog.occurred_at >= start_today)
        .scalar()
        or 0
    )
    yesterday_errors = (
        db.query(func.count(EquipmentLog.log_id))
        .filter(
            EquipmentLog.status != "정상",
            EquipmentLog.occurred_at >= start_yesterday,
            EquipmentLog.occurred_at < start_today,
        )
        .scalar()
        or 0
    )

    unhandled = (
        db.query(func.count(Notification.notification_id))
        .filter(Notification.is_read == ReadStatus.UNREAD)
        .scalar()
        or 0
    )
    total_noti = db.query(func.count(Notification.notification_id)).scalar() or 0

    avg_duration = (
        db.query(func.avg(ActionLog.duration))
        .filter(ActionLog.duration.is_not(None))
        .scalar()
    )

    manual_count = db.query(func.count(SavedManual.manual_id)).scalar() or 0
    error_code_count = db.query(func.count(ErrorCode.error_code_id)).scalar() or 0

    # 시간대별 24h 추이 (2시간 간격, hour=00,02,...,22)
    trend_rows = (
        db.query(
            func.to_char(EquipmentLog.occurred_at, "HH24").label("hour"),
            func.count(EquipmentLog.log_id),
        )
        .filter(
            EquipmentLog.status != "정상",
            EquipmentLog.occurred_at >= now - timedelta(hours=24),
        )
        .group_by("hour")
        .all()
    )
    counts_by_hour = {int(row[0]): int(row[1]) for row in trend_rows}
    hourly_trend = [
        HourlyPoint(hour=f"{h:02d}", count=counts_by_hour.get(h, 0))
        for h in range(0, 24, 2)
    ]

    # Top N 이상징후 (미확인 + 긴급/경고 우선)
    digest_rows = (
        db.query(
            Notification.notification_id,
            Notification.message,
            Notification.level,
            Notification.occured_at,
            EquipmentLog.value,
            EquipmentLog.data_type,
            Equipment.equipment_code,
        )
        .join(EquipmentLog, EquipmentLog.log_id == Notification.log_id)
        .join(Equipment, Equipment.equipment_id == EquipmentLog.equipment_id)
        .filter(Notification.is_read == ReadStatus.UNREAD)
        .order_by(Notification.notification_id.desc())
        .limit(5)
        .all()
    )
    anomaly_digest = [
        AnomalyDigest(
            notification_id=r[0],
            title=f"{r[6]} {r[5].value if hasattr(r[5], 'value') else r[5]} 이상",
            level=r[2],
            meta=f"{r[5].value if hasattr(r[5], 'value') else r[5]}: {r[4]:.1f}",
            occurred_at=r[3],
            equipment_code=r[6],
        )
        for r in digest_rows
    ]

    return DashboardSummary(
        stats=StatCardData(
            todayErrorCount=today_errors,
            yesterdayErrorCount=yesterday_errors,
            unhandledNotificationCount=unhandled,
            totalNotificationCount=total_noti,
            avgActionDurationMinutes=float(avg_duration) if avg_duration is not None else None,
            manualCount=manual_count,
            errorCodeCount=error_code_count,
        ),
        hourly_trend=hourly_trend,
        anomaly_digest=anomaly_digest,
    )
