import { dashboardApi } from './dashboard.api';
import type { DashboardRepository } from '../domain/dashboard.repository';

export const dashboardRepositoryImpl: DashboardRepository = {
  getSummary: dashboardApi.getSummary,
};
