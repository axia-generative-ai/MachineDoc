import { ChevronRight } from 'lucide-react';

import { anomalyItems } from '../model/dashboardData';
import { colorClasses, type DashboardColor } from '../model/dashboardTheme';
import { Panel } from '../../../shared/ui/Panel';

export function AnomalyList() {
  return (
    <Panel className="p-5 lg:col-span-5">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-[22px] font-extrabold tracking-[-0.04em]">확인 필요 이상징후</h2>
        <ChevronRight className="h-7 w-7 text-slate-400" />
      </div>
      <div className="divide-y divide-slate-700/70">
        {anomalyItems.map((item) => {
          const Icon = item.icon;
          const palette = colorClasses[item.color as DashboardColor];

          return (
            <article
              key={`${item.title}-${item.time}`}
              className="grid grid-cols-[48px_minmax(0,1fr)_84px_120px_72px] items-center gap-5 py-5 first:pt-2"
            >
              <div className={`grid h-12 w-12 place-items-center rounded-full ${palette.bg}`}>
                <Icon className={`h-7 w-7 ${palette.text}`} />
              </div>
              <h3 className="truncate text-[19px] font-bold tracking-[-0.04em] text-white">{item.title}</h3>
              <span className={`grid h-10 w-[64px] place-items-center rounded-md text-[17px] font-black ${palette.badge}`}>{item.level}</span>
              <span className="whitespace-nowrap text-[15px] font-medium text-slate-400">{item.meta}</span>
              <span className="whitespace-nowrap text-right pr-[10px] text-[15px] font-medium text-slate-400">{item.time}</span>
            </article>
          );
        })}
      </div>
    </Panel>
  );
}
