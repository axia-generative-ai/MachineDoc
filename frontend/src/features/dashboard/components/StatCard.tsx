import type { stats } from '../model/dashboardData';
import { colorClasses, type DashboardColor } from '../model/dashboardTheme';
import { Panel } from '../../../shared/ui/Panel';

type StatCardProps = {
  stat: (typeof stats)[number];
};

export function StatCard({ stat }: StatCardProps) {
  const Icon = stat.icon;
  const palette = colorClasses[stat.color as DashboardColor];

  return (
    <Panel className="flex min-h-[150px] items-center gap-6 p-5 transition duration-300 hover:-translate-y-1 hover:border-blue-400/45 hover:bg-slate-900/45">
      <div className={`grid h-20 w-20 shrink-0 place-items-center rounded-full ${palette.bg} ring-1 ${palette.ring}`}>
        <Icon className={`h-11 w-11 ${palette.text}`} strokeWidth={2.4} />
      </div>
      <div>
        <p className={`text-[42px] font-black leading-none tracking-[-0.07em] ${palette.text}`}>
          {stat.value}
          <span className="ml-1 text-[24px]">{stat.unit}</span>
        </p>
        <p className="mt-2 text-[22px] font-bold tracking-[-0.04em] text-white">{stat.label}</p>
        <p className="mt-3 text-[16px] font-semibold text-slate-400">
          {stat.caption} <span className={palette.text}>{stat.accent}</span>
        </p>
      </div>
    </Panel>
  );
}
