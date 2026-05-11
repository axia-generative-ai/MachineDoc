import { useEffect, useState } from 'react';

import { dashboardRepositoryImpl } from '../infra/dashboard.repository.impl';
import type { DashboardSummary } from '../model/dashboard.types';
import { getDashboardSummaryUseCase } from '../usecase/getDashboardSummary.usecase';

export function useDashboardSummary() {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    setIsLoading(true);
    setErrorMessage(null);

    getDashboardSummaryUseCase(dashboardRepositoryImpl)
      .then((data) => {
        if (!cancelled) setSummary(data);
      })
      .catch((error) => {
        if (!cancelled) setErrorMessage(error?.message ?? '대시보드 정보를 불러오지 못했습니다.');
      })
      .finally(() => {
        if (!cancelled) setIsLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, []);

  return {
    summary,
    isLoading,
    errorMessage,
  };
}
