import { Download, Save } from 'lucide-react';

import { alertFilters } from '../model/alertLogData';

type AlertLogHeaderProps = {
  selectedFilter?: string;
};

export function AlertLogHeader({ selectedFilter = '전체' }: AlertLogHeaderProps) {
  return (
    <div className="mb-6">
      <h1 className="text-[40px] font-black tracking-[-0.06em] text-white">알림 로그</h1>

      <div className="mt-6 flex flex-col gap-4 xl:flex-row xl:items-center xl:justify-between">
        <div className="flex flex-wrap gap-3">
          {alertFilters.map((filter) => {
            const isActive = filter === selectedFilter;

            return (
              <button
                key={filter}
                type="button"
                className={`h-[52px] min-w-[92px] rounded-lg border px-6 text-[20px] font-black tracking-[-0.04em] transition ${
                  isActive
                    ? 'border-blue-500 bg-blue-600 text-white shadow-[0_0_24px_rgba(37,99,235,0.35)]'
                    : 'border-slate-700 bg-slate-950/25 text-slate-200 hover:border-blue-400/50 hover:text-blue-300'
                }`}
              >
                {filter}
              </button>
            );
          })}
        </div>

        <div className="flex flex-wrap gap-3">
          <button
            type="button"
            className="flex h-[52px] items-center gap-3 rounded-lg border border-blue-500 bg-blue-500/5 px-7 text-[19px] font-black tracking-[-0.04em] text-blue-400 transition hover:bg-blue-500/15"
          >
            <Save className="h-6 w-6" />
            저장
          </button>
          <button
            type="button"
            className="flex h-[52px] items-center gap-3 rounded-lg border border-blue-600 bg-blue-600 px-7 text-[19px] font-black tracking-[-0.04em] text-white shadow-[0_0_26px_rgba(37,99,235,0.35)] transition hover:bg-blue-500"
          >
            <Download className="h-6 w-6" />
            내보내기
          </button>
        </div>
      </div>
    </div>
  );
}
