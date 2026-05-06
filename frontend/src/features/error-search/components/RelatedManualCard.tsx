import { ChevronRight } from 'lucide-react';

import { relatedManuals } from '../model/errorSearchData';
import { Panel } from '../../../shared/ui/Panel';

type RelatedManualCardProps = {
  manual: (typeof relatedManuals)[number];
};

export function RelatedManualCard({ manual }: RelatedManualCardProps) {
  const Icon = manual.icon;

  return (
    <Panel className="flex min-h-[132px] items-center gap-5 p-5 transition hover:-translate-y-1 hover:border-blue-400/50 hover:bg-slate-900/40">
      <div className="grid h-16 w-16 shrink-0 place-items-center rounded-full bg-blue-500/10 text-blue-400">
        <Icon className="h-8 w-8" />
      </div>

      <div className="min-w-0 flex-1">
        <div className="mb-5 flex items-center gap-3">
          <h3 className="truncate text-[19px] font-extrabold tracking-[-0.04em] text-white">{manual.title}</h3>
          <span className="rounded-md bg-red-500/15 px-2 py-1 text-[13px] font-black text-red-300">{manual.type}</span>
        </div>
        <div className="flex items-center gap-4">
          <div className="h-2.5 flex-1 overflow-hidden rounded-full bg-slate-700/70">
            <div className="h-full rounded-full bg-blue-500 shadow-[0_0_14px_rgba(59,130,246,0.75)]" style={{ width: `${manual.matchRate}%` }} />
          </div>
          <span className="w-14 text-right text-[21px] font-black text-blue-500">{manual.matchRate}%</span>
        </div>
      </div>

      <ChevronRight className="h-7 w-7 shrink-0 text-slate-200" />
    </Panel>
  );
}
