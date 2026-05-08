import { ChevronLeft, ChevronRight } from 'lucide-react';

export function SearchHistoryPagination() {
  return (
    <div className="mt-5 flex items-center justify-center gap-2 text-[14px] font-black text-slate-500">
      <button type="button" className="grid h-8 w-8 place-items-center rounded-lg transition hover:bg-slate-800 hover:text-blue-300">
        <ChevronLeft className="h-4 w-4" />
      </button>
      {[1, 2, 3].map((page) => (
        <button
          key={page}
          type="button"
          className={`grid h-8 w-8 place-items-center rounded-lg transition ${
            page === 1 ? 'bg-blue-600 text-white shadow-[0_0_18px_rgba(37,99,235,0.34)]' : 'hover:bg-slate-800 hover:text-blue-300'
          }`}
        >
          {page}
        </button>
      ))}
      <button type="button" className="grid h-8 w-8 place-items-center rounded-lg transition hover:bg-slate-800 hover:text-blue-300">
        <ChevronRight className="h-4 w-4" />
      </button>
    </div>
  );
}
