import { Bot, CheckCircle2, Wrench } from 'lucide-react';

import type { ErrorSearchResult } from '../../model/errorSearch.types';
import { Panel } from '../../../../shared/ui/Panel';

type ErrorSearchAiSummaryProps = {
  result: ErrorSearchResult;
};

export function ErrorSearchAiSummary({ result }: ErrorSearchAiSummaryProps) {
  return (
    <Panel className="mb-6 p-5">
      <div className="flex flex-col gap-5 lg:flex-row lg:items-stretch">
        <div className="flex items-center gap-4 lg:w-[260px]">
          <div className="grid h-14 w-14 shrink-0 place-items-center rounded-full bg-blue-500/10 text-blue-400 shadow-[0_0_24px_rgba(37,99,235,0.22)]">
            <Bot className="h-8 w-8" />
          </div>
          <div>
            <p className="text-[13px] font-black tracking-[0.18em] text-blue-300">AI RESULT</p>
            <h2 className="mt-1 text-[22px] font-black tracking-[-0.05em] text-white">{result.keyword}</h2>
            <p className="mt-1 text-[14px] font-semibold text-emerald-300">{result.status}</p>
          </div>
        </div>

        <div className="grid flex-1 gap-4 md:grid-cols-2">
          <article className="rounded-xl border border-slate-700/80 bg-slate-950/35 p-4">
            <div className="mb-3 flex items-center gap-2 text-blue-300">
              <CheckCircle2 className="h-5 w-5" />
              <h3 className="text-[16px] font-black">분석 결과</h3>
            </div>
            <p className="text-[15px] font-semibold leading-7 text-slate-300">{result.analysis}</p>
          </article>

          <article className="rounded-xl border border-slate-700/80 bg-slate-950/35 p-4">
            <div className="mb-3 flex items-center gap-2 text-orange-300">
              <Wrench className="h-5 w-5" />
              <h3 className="text-[16px] font-black">권장 조치</h3>
            </div>
            <p className="text-[15px] font-semibold leading-7 text-slate-300">{result.solution}</p>
          </article>
        </div>
      </div>
    </Panel>
  );
}
