import type { DashboardRepository } from '../domain/dashboard.repository';

export function getDashboardSummaryUseCase(repository: DashboardRepository) {
  return repository.getSummary();
}
