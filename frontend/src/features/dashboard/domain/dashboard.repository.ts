import type { DashboardSummary } from '../model/dashboard.types';

export type DashboardRepository = {
  getSummary(): Promise<DashboardSummary>;
};
