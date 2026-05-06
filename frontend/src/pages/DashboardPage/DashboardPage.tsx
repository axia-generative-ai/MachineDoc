import { AnomalyList } from '../../features/dashboard/components/AnomalyList';
import { StatCard } from '../../features/dashboard/components/StatCard';
import { TrendChart } from '../../features/dashboard/components/TrendChart';
import { stats } from '../../features/dashboard/model/dashboardData';

export function DashboardPage() {
  return (
    <div className="mx-auto max-w-[1640px]">
      <div className="mb-5">
        <h1 className="text-[40px] font-black tracking-[-0.06em] text-white">대시보드</h1>
        <p className="mt-1 text-[18px] font-semibold tracking-[-0.04em] text-slate-400">오늘 2026-04-28 · 라인A·B·C 전체</p>
      </div>

      <div className="grid gap-5 md:grid-cols-2 2xl:grid-cols-4">
        {stats.map((stat) => (
          <StatCard key={stat.label} stat={stat} />
        ))}
      </div>

      <div className="mt-6 grid gap-5 lg:grid-cols-12">
        <TrendChart />
        <AnomalyList />
      </div>
    </div>
  );
}
