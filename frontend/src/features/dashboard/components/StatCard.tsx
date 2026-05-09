import type { LucideIcon } from 'lucide-react';

import { Panel } from '../../../shared/ui/Panel';
import { colorClasses, type DashboardColor } from '../model/dashboardTheme';

export type StatCardData = {
  label: string;
  value: string;
  unit: string;
  caption: string;
  accent: string;
  color: DashboardColor;
  icon: LucideIcon;
};

type StatCardProps = {
  stat: StatCardData;
};

export function StatCard({ stat }: StatCardProps) {
  const Icon = stat.icon;
  const palette = colorClasses[stat.color];

  return (
    <Panel className="flex min-h-[150px] items-center gap-6 p-5 transition duration-300 hover:-translate-y-1 hover:border-blue-400/45 hover:bg-slate-900/45">
      <div className={`grid h-20 w-20 shrink-0 place-items-center rounded-full ${palette.bg} ring-1 ${palette.ring}`}>
        <Icon className={`h-11 w-11 ${palette.text}`} strokeWidth={2.4} />
      </div>
      <div>
        <p className={`text-[42px] font-black leading-none ${palette.text}`}>
          {stat.value}
          <span className="ml-1 text-[24px]">{stat.unit}</span>
        </p>
        <p className="mt-2 text-[22px] font-bold text-white">{stat.label}</p>
        <p className="mt-3 text-[16px] font-semibold text-slate-400">
          {stat.caption} <span className={palette.text}>{stat.accent}</span>
        </p>
      </div>
    </Panel>
  );
}
