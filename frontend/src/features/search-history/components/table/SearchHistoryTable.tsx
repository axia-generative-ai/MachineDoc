import { CheckCircle2, Clock3, XCircle } from 'lucide-react';

import { searchHistoryItems, type SearchHistoryStatus } from '../../model/searchHistoryData';

const statusStyles: Record<SearchHistoryStatus, { label: string; className: string; icon: typeof CheckCircle2 }> = {
  COMPLETED: {
    label: '완료',
    className: 'border-emerald-400/40 bg-emerald-500/10 text-emerald-300',
    icon: CheckCircle2,
  },
  INVALID_CODE: {
    label: '코드 없음',
    className: 'border-amber-400/40 bg-amber-500/10 text-amber-300',
    icon: Clock3,
  },
  AI_ERROR: {
    label: 'AI 오류',
    className: 'border-red-400/40 bg-red-500/10 text-red-300',
    icon: XCircle,
  },
};

export function SearchHistoryTable() {
  return (
    <div className="mt-5 overflow-hidden rounded-2xl border border-slate-700/80 bg-slate-950/25">
      <div className="grid grid-cols-[170px_1fr_1.4fr_130px] border-b border-slate-700/80 bg-slate-900/60 px-6 py-4 text-[14px] font-black text-slate-400 max-lg:hidden">
        <span>날짜</span>
        <span>검색어</span>
        <span>결과</span>
        <span className="text-right">상태</span>
      </div>

      <div className="divide-y divide-slate-800/90">
        {searchHistoryItems.map((item) => {
          const status = statusStyles[item.status];
          const StatusIcon = status.icon;

          return (
            <article
              key={item.id}
              className="grid gap-3 px-5 py-5 transition hover:bg-blue-500/[0.04] lg:grid-cols-[170px_1fr_1.4fr_130px] lg:items-center lg:px-6"
            >
              <div>
                <p className="text-[13px] font-bold text-slate-500 lg:hidden">날짜</p>
                <p className="text-[15px] font-semibold text-slate-300">{item.createdAt}</p>
              </div>

              <div>
                <p className="text-[13px] font-bold text-slate-500 lg:hidden">검색어</p>
                <p className="text-[17px] font-black tracking-[-0.04em] text-white">{item.keyword}</p>
              </div>

              <div>
                <p className="text-[13px] font-bold text-slate-500 lg:hidden">결과</p>
                <p className="text-[15px] font-semibold text-slate-300">{item.result}</p>
              </div>

              <div className="flex lg:justify-end">
                <span className={`inline-flex h-9 items-center gap-2 rounded-lg border px-3 text-[14px] font-black ${status.className}`}>
                  <StatusIcon className="h-4 w-4" />
                  {status.label}
                </span>
              </div>
            </article>
          );
        })}
      </div>
    </div>
  );
}

