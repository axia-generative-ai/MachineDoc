import { apiClient } from '../../../shared/api/apiClient';
import type { DashboardAnomalyDigest, DashboardAnomalyLevel, DashboardHourlyPoint, DashboardStats, DashboardSummary } from '../model/dashboard.types';

type BackendDashboardSummary = {
  stats: DashboardStats;
  hourly_trend: DashboardHourlyPoint[];
  anomaly_digest: {
    notification_id: number;
    title: string;
    level: DashboardAnomalyLevel | string;
    meta: string;
    occurred_at: string;
    equipment_code: string;
  }[];
};

function mapAnomalyLevel(level: string): DashboardAnomalyLevel {
  if (level === '긴급' || level.toUpperCase() === 'URGENT') return '긴급';
  if (level === '경고' || level.toUpperCase() === 'WARNING' || level.toUpperCase() === 'WARN') return '경고';
  return '주의';
}

function mapAnomalyDigest(row: BackendDashboardSummary['anomaly_digest'][number]): DashboardAnomalyDigest {
  return {
    notificationId: row.notification_id,
    title: row.title,
    level: mapAnomalyLevel(row.level),
    meta: row.meta,
    occurredAt: row.occurred_at,
    equipmentCode: row.equipment_code,
  };
}

export const dashboardApi = {
  async getSummary(): Promise<DashboardSummary> {
    const { data } = await apiClient.get<BackendDashboardSummary>('/dashboard/summary');

    return {
      stats: data.stats,
      hourlyTrend: data.hourly_trend,
      anomalyDigest: data.anomaly_digest.map(mapAnomalyDigest),
    };
  },
};
