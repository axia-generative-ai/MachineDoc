import { apiClient } from '../../../shared/api/apiClient';

export type DashboardStats = {
  todayErrorCount: number;
  yesterdayErrorCount: number;
  unhandledNotificationCount: number;
  totalNotificationCount: number;
  avgActionDurationMinutes: number | null;
  actionGoalMinutes: number;
  manualCount: number;
  errorCodeCount: number;
};

export type DashboardHourlyPoint = {
  hour: string;
  count: number;
};

export type DashboardAnomalyDigest = {
  notificationId: number;
  title: string;
  level: '긴급' | '경고' | '주의';
  meta: string;
  occurredAt: string;
  equipmentCode: string;
};

export type DashboardSummary = {
  stats: DashboardStats;
  hourlyTrend: DashboardHourlyPoint[];
  anomalyDigest: DashboardAnomalyDigest[];
};

type BackendDashboardSummary = {
  stats: DashboardStats;
  hourly_trend: DashboardHourlyPoint[];
  anomaly_digest: {
    notification_id: number;
    title: string;
    level: DashboardAnomalyDigest['level'];
    meta: string;
    occurred_at: string;
    equipment_code: string;
  }[];
};

export const dashboardApi = {
  async getSummary(): Promise<DashboardSummary> {
    const { data } = await apiClient.get<BackendDashboardSummary>('/dashboard/summary');
    return {
      stats: data.stats,
      hourlyTrend: data.hourly_trend,
      anomalyDigest: data.anomaly_digest.map((row) => ({
        notificationId: row.notification_id,
        title: row.title,
        level: row.level,
        meta: row.meta,
        occurredAt: row.occurred_at,
        equipmentCode: row.equipment_code,
      })),
    };
  },
};
