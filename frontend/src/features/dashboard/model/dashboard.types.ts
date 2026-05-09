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

export type DashboardAnomalyLevel = '긴급' | '경고' | '주의';

export type DashboardAnomalyDigest = {
  notificationId: number;
  title: string;
  level: DashboardAnomalyLevel;
  meta: string;
  occurredAt: string;
  equipmentCode: string;
};

export type DashboardSummary = {
  stats: DashboardStats;
  hourlyTrend: DashboardHourlyPoint[];
  anomalyDigest: DashboardAnomalyDigest[];
};
