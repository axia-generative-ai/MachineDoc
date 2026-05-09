import { Clock3 } from 'lucide-react';

import { recentSearches, type RecentSearchItem } from '../../model/errorSearchHomeData';
import { Panel } from '../../../../shared/ui/Panel';

export function RecentSearchPanel() {
  return (
    <Panel className="p-5">
      <div className="mb-4 flex items-center gap-3">
        <Clock3 className="h-6 w-6 text-blue-400" />
        <h2 className="text-[22px] font-black tracking-[-0.05em] text-white">최근 검색</h2>
      </div>

      <div className="divide-y divide-slate-800/90">
        {recentSearches.map((item: RecentSearchItem) => (
          <button key={item.keyword} type="button" className="flex w-full items-center justify-between gap-4 py-4 text-left transition hover:text-blue-300">
            <span className="truncate text-[17px] font-bold text-slate-200">{item.keyword}</span>
            <span className="shrink-0 text-[14px] font-semibold text-slate-500">{item.time}</span>
          </button>
        ))}
      </div>
    </Panel>
  );
}

