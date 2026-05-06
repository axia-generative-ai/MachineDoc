import { adminTabs } from '../model/adminData';

type AdminTabsProps = {
  activeTab?: string;
};

export function AdminTabs({ activeTab = '매뉴얼 등록' }: AdminTabsProps) {
  return (
    <div className="mb-6 overflow-hidden rounded-2xl border border-slate-700/80 bg-slate-950/25">
      <div className="grid grid-cols-2 md:grid-cols-4">
        {adminTabs.map((tab) => {
          const isActive = tab === activeTab;

          return (
            <button
              key={tab}
              type="button"
              className={`relative h-16 text-[19px] font-bold tracking-[-0.04em] transition ${
                isActive ? 'text-blue-400' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              {tab}
              {isActive && <span className="absolute bottom-0 left-0 h-1 w-full bg-blue-500 shadow-[0_0_18px_rgba(59,130,246,0.75)]" />}
            </button>
          );
        })}
      </div>
    </div>
  );
}
