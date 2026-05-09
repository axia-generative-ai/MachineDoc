import { AlertTriangle, BookOpen } from 'lucide-react';

import { useDashboardSummary } from '../../dashboard/hooks/useDashboardSummary';
import { adminStatColorClasses, type AdminStatColor } from '../model/adminTheme';

type AdminStat = {
  value: string;
  unit: string;
  label: string;
  icon: typeof BookOpen;
  color: AdminStatColor;
};

export function AdminStatsGrid() {
  const { summary } = useDashboardSummary();

  const stats: AdminStat[] = summary
    ? [
        {
          value: String(summary.stats.manualCount),
          unit: '종',
          label: '등록 매뉴얼',
          icon: BookOpen,
          color: 'green',
        },
        {
          value: String(summary.stats.errorCodeCount),
          unit: '개',
          label: '오류코드',
          icon: AlertTriangle,
          color: 'red',
        },
      ]
    : [];

  return (
    <div className="grid gap-4 md:grid-cols-2">
      {stats.map((stat) => {
        const Icon = stat.icon;
        const palette = adminStatColorClasses[stat.color];

        return (
          <article key={stat.label} className="flex min-h-[120px] items-center justify-between rounded-xl border border-slate-700/80 bg-slate-950/20 p-5">
            <div>
              <p className={`text-[42px] font-black leading-none ${palette.text}`}>
                {stat.value}
                <span className="ml-1 text-[20px]">{stat.unit}</span>
              </p>
              <p className="mt-3 text-[16px] font-bold text-slate-200">{stat.label}</p>
            </div>
            <div className={`grid h-16 w-16 place-items-center rounded-full ${palette.bg}`}>
              <Icon className={`h-9 w-9 ${palette.icon}`} />
            </div>
          </article>
        );
      })}
    </div>
  );
}
