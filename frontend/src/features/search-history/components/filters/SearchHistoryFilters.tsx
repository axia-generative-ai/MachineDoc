import { CalendarDays, Search, SlidersHorizontal } from 'lucide-react';

export function SearchHistoryFilters() {
  return (
    <div className="mt-5 grid gap-3 lg:grid-cols-[1fr_180px_180px]">
      <label className="flex h-12 items-center gap-3 rounded-xl border border-slate-700 bg-slate-950/35 px-4 text-slate-400 transition focus-within:border-blue-400/70">
        <Search className="h-5 w-5" />
        <input
          className="h-full min-w-0 flex-1 bg-transparent text-[15px] font-semibold text-white outline-none placeholder:text-slate-500"
          placeholder="검색어를 입력하세요"
        />
      </label>

      <button
        type="button"
        className="flex h-12 items-center justify-between rounded-xl border border-slate-700 bg-slate-950/35 px-4 text-[15px] font-bold text-slate-300 transition hover:border-blue-400/70 hover:text-blue-300"
      >
        <span className="flex items-center gap-2">
          <CalendarDays className="h-5 w-5" />
          기간 선택
        </span>
        <span className="text-slate-500">▾</span>
      </button>

      <button
        type="button"
        className="flex h-12 items-center justify-between rounded-xl border border-slate-700 bg-slate-950/35 px-4 text-[15px] font-bold text-slate-300 transition hover:border-blue-400/70 hover:text-blue-300"
      >
        <span className="flex items-center gap-2">
          <SlidersHorizontal className="h-5 w-5" />
          상태
        </span>
        <span className="text-slate-500">▾</span>
      </button>
    </div>
  );
}
