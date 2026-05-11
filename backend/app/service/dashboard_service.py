from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.crud.crud_dashboard import dashboard_repository
from app.schemas.dashboard import DashboardSummary, StatCardData, HourlyPoint, AnomalyDigest

class DashboardService:
    def _today_window(self):
        now = datetime.now()
        start_today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        start_yesterday = start_today - timedelta(days=1)
        return start_today, start_yesterday, now

    def get_summary(self, db: Session) -> DashboardSummary:
        start_today, start_yesterday, now = self._today_window()

        # 1. 통계 카드 데이터 조회
        today_errors = dashboard_repository.get_error_count(db, start_today)
        yesterday_errors = dashboard_repository.get_error_count(db, start_yesterday, start_today)
        unhandled, total_noti = dashboard_repository.get_notification_counts(db)
        avg_duration = dashboard_repository.get_avg_action_duration(db)
        manual_count, error_code_count = dashboard_repository.get_resource_counts(db)

        # 2. 시간대별 추이 가공 (2시간 간격)
        trend_rows = dashboard_repository.get_hourly_trend_rows(db, now - timedelta(hours=24))
        counts_by_hour = {int(row[0]): int(row[1]) for row in trend_rows}
        hourly_trend = [
            HourlyPoint(hour=f"{h:02d}", count=counts_by_hour.get(h, 0))
            for h in range(0, 24, 2)
        ]

        # 3. 이상징후 요약 가공
        digest_rows = dashboard_repository.get_recent_anomalies(db)
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

dashboard_service = DashboardService()