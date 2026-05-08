import { searchHistoryTabs } from '../../model/searchHistoryData';

export function SearchHistoryTabs() {
  return (
    <div className="grid gap-3 md:grid-cols-3">
      {searchHistoryTabs.map((tab, index) => {
        const isActive = index === 0;

        return (
          <button
            key={tab}
            type="button"
            className={`h-12 rounded-xl border text-[16px] font-black tracking-[-0.04em] transition ${
              isActive
                ? 'border-blue-400 bg-blue-600/15 text-blue-300 shadow-[0_0_24px_rgba(37,99,235,0.24)]'
                : 'border-slate-700 bg-slate-950/30 text-slate-400 hover:border-blue-400/60 hover:text-blue-300'
            }`}
          >
            {tab}
          </button>
        );
      })}
    </div>
  );
}



