import type { HistoryTab } from '../layout/SearchHistoryPanel';

const TABS: HistoryTab[] = ['검색 이력', '조치 이력', '저장 문서'];

type Props = {
  activeTab: HistoryTab;
  onTabChange: (tab: HistoryTab) => void;
};

export function SearchHistoryTabs({ activeTab, onTabChange }: Props) {
  return (
    <div className="grid gap-3 md:grid-cols-3">
      {TABS.map((tab) => {
        const isActive = tab === activeTab;

        return (
          <button
            key={tab}
            type="button"
            onClick={() => onTabChange(tab)}
            className={`h-12 rounded-xl border text-[16px] font-black transition ${
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
