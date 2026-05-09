import { ChevronRight, FileText } from 'lucide-react';

import { Panel } from '../../../../shared/ui/Panel';
import type { ManualSummary } from '../../infra/manual.api';

type RelatedManualCardProps = {
  manual: ManualSummary;
  isSelected: boolean;
  onSelect: (manual: ManualSummary) => void;
};

export function RelatedManualCard({ manual, isSelected, onSelect }: RelatedManualCardProps) {
  return (
    <button className="text-left" type="button" onClick={() => onSelect(manual)}>
      <Panel
        className={`flex min-h-[132px] items-center gap-5 p-5 transition hover:-translate-y-1 hover:border-blue-400/50 hover:bg-slate-900/40 ${
          isSelected ? 'border-blue-400/70 bg-blue-500/10' : ''
        }`}
      >
        <div className="grid h-16 w-16 shrink-0 place-items-center rounded-full bg-blue-500/10 text-blue-400">
          <FileText className="h-8 w-8" />
        </div>

        <div className="min-w-0 flex-1">
          <div className="mb-4 flex items-center gap-3">
            <h3 className="truncate text-[19px] font-extrabold text-white">{manual.title}</h3>
            <span className="rounded-md bg-blue-500/15 px-2 py-1 text-[13px] font-black text-blue-200">{manual.category}</span>
          </div>
          <p className="text-[14px] font-medium text-slate-400">버전 {manual.version}</p>
        </div>

        <ChevronRight className="h-7 w-7 shrink-0 text-slate-200" />
      </Panel>
    </button>
  );
}
