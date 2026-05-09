import { useEffect, useState } from 'react';
import { AlertTriangle, Bell, BookOpen, Clock3 } from 'lucide-react';

import { AnomalyList } from '../../features/dashboard/components/AnomalyList';
import { StatCard, type StatCardData } from '../../features/dashboard/components/StatCard';
import { TrendChart } from '../../features/dashboard/components/TrendChart';
import { dashboardApi, type DashboardSummary } from '../../features/dashboard/infra/dashboard.api';

function buildStatCards(summary: DashboardSummary): StatCardData[] {
  const { stats } = summary;
  const diff = stats.todayErrorCount - stats.yesterdayErrorCount;
  const diffLabel = diff === 0 ? '동일' : diff > 0 ? `+${diff}` : `${diff}`;

  return [
    {
      label: '금일 오류 발생',
      value: String(stats.todayErrorCount),
      unit: '건',
      caption: '어제 대비',
      accent: diffLabel,
      color: 'red',
      icon: AlertTriangle,
    },
    {
      label: '미확인 알림',
      value: String(stats.unhandledNotificationCount),
      unit: '건',
      caption: '전체',
      accent: `${stats.totalNotificationCount}건`,
      color: 'amber',
      icon: Bell,
    },
    {
      label: '평균 조치 시간',
      value: stats.avgActionDurationMinutes != null ? stats.avgActionDurationMinutes.toFixed(1) : '-',
      unit: '분',
      caption: '목표',
      accent: `${stats.actionGoalMinutes}분 이내`,
      color: 'green',
      icon: Clock3,
    },
    {
      label: '등록 매뉴얼',
      value: String(stats.manualCount),
      unit: '종',
      caption: '오류코드',
      accent: `${stats.errorCodeCount}개`,
      color: 'blue',
      icon: BookOpen,
    },
  ];
}

export function DashboardPage() {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    dashboardApi
      .getSummary()
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

  const today = new Date().toLocaleDateString('ko-KR');
  const cards = summary ? buildStatCards(summary) : [];

  return (
    <div className="mx-auto max-w-[1640px]">
      <div className="mb-5">
        <h1 className="text-[40px] font-black tracking-[-0.06em] text-white">대시보드</h1>
        <p className="mt-1 text-[18px] font-semibold tracking-[-0.04em] text-slate-400">
          오늘 {today} · 라인A·B·C 전체
        </p>
      </div>

      {errorMessage && (
        <p className="mb-5 rounded-lg border border-red-500/40 bg-red-500/10 px-4 py-3 text-[14px] font-bold text-red-300">
          {errorMessage}
        </p>
      )}

      {isLoading ? (
        <p className="py-12 text-center text-[15px] font-bold text-slate-400">대시보드를 불러오는 중...</p>
      ) : (
        <>
          <div className="grid gap-5 md:grid-cols-2 2xl:grid-cols-4">
            {cards.map((stat) => (
              <StatCard key={stat.label} stat={stat} />
            ))}
          </div>

          <div className="mt-6 grid gap-5 lg:grid-cols-12">
            <TrendChart points={summary?.hourlyTrend ?? []} />
            <AnomalyList items={summary?.anomalyDigest ?? []} />
          </div>
        </>
      )}
    </div>
  );
}
