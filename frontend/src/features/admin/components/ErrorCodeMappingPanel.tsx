import { errorCodeMappings } from '../model/adminData';
import { Panel } from '../../../shared/ui/Panel';
import { AdminStatsGrid } from './AdminStatsGrid';

export function ErrorCodeMappingPanel() {
  return (
    <Panel className="overflow-hidden p-6 lg:col-span-7">
      <h2 className="text-[24px] font-black tracking-[-0.05em] text-white">오류코드 매핑</h2>

      <div className="mt-6 overflow-hidden rounded-xl border border-slate-700/80">
        {errorCodeMappings.map((item) => {
          const Icon = item.icon;

          return (
            <button
              key={item.code}
              type="button"
              className="grid h-20 w-full grid-cols-[130px_1fr_32px] items-center border-b border-slate-700/80 px-6 text-left last:border-b-0 transition hover:bg-white/[0.03]"
            >
              <span className="text-[20px] font-semibold text-white">{item.code}</span>
              <span className="text-[20px] font-semibold text-slate-300">{item.manual}</span>
              <Icon className="h-6 w-6 text-slate-400" />
            </button>
          );
        })}
      </div>

      <div className="mt-8 border-t border-slate-700/80 pt-6">
        <AdminStatsGrid />
      </div>
    </Panel>
  );
}
