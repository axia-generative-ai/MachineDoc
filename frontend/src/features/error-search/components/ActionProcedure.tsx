import { actionSteps } from '../model/errorSearchData';
import { Panel } from '../../../shared/ui/Panel';

export function ActionProcedure() {
  return (
    <Panel className="min-h-[455px] p-6 lg:col-span-5">
      <h2 className="text-[28px] font-black tracking-[-0.05em] text-white">AI 조치 절차</h2>

      <div className="mt-6 divide-y divide-slate-700/80">
        {actionSteps.map((item) => {
          const Icon = item.icon;

          return (
            <article key={item.step} className="grid grid-cols-[44px_64px_1fr] items-center gap-5 py-5 first:pt-0 last:pb-0">
              <span className="grid h-10 w-10 place-items-center rounded-full bg-blue-600 text-[17px] font-black text-white shadow-[0_0_20px_rgba(37,99,235,0.35)]">
                {item.step}
              </span>
              <span className="grid h-14 w-14 place-items-center rounded-full bg-blue-500/10 text-blue-400">
                <Icon className="h-7 w-7" />
              </span>
              <p className="text-[19px] font-semibold tracking-[-0.04em] text-white">{item.title}</p>
            </article>
          );
        })}
      </div>
    </Panel>
  );
}
