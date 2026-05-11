import { Wrench } from 'lucide-react';

import type { ErrorSearchResult } from '../../model/errorSearch.types';
import { Panel } from '../../../../shared/ui/Panel';

type Step = {
  step: number;
  title: string;
  source?: string;
};

// solution 텍스트는 ai-service가 "1. 동작 (출처: file.pdf p12)\n2. ..." 형식으로 채워서 보냄.
// 빈 줄/번호 없는 줄은 무시. (출처: ...) 부분은 별도로 분리해 보조 라벨로 표시.
const STEP_RE = /^\s*(\d+)[.)]\s*(.+?)\s*$/;
const SOURCE_RE = /\s*\(출처:\s*([^)]+)\)\s*$/;

function parseSteps(solution: string): Step[] {
  const lines = solution.split(/\r?\n/);
  const steps: Step[] = [];
  for (const line of lines) {
    const match = STEP_RE.exec(line);
    if (!match) continue;
    let title = match[2].trim();
    let source: string | undefined;
    const srcMatch = SOURCE_RE.exec(title);
    if (srcMatch) {
      source = srcMatch[1].trim();
      title = title.replace(SOURCE_RE, '').trim();
    }
    steps.push({ step: Number(match[1]), title, source });
  }
  return steps;
}

type Props = {
  result: ErrorSearchResult | null;
};

export function ActionProcedure({ result }: Props) {
  const steps = result ? parseSteps(result.solution) : [];

  return (
    <Panel className="min-h-[455px] p-6 lg:col-span-5">
      <h2 className="text-[28px] font-black tracking-[-0.05em] text-white">AI 조치 절차</h2>

      {steps.length === 0 ? (
        <p className="mt-6 rounded-xl border border-slate-700/80 bg-slate-950/20 px-5 py-10 text-center text-[14px] font-bold text-slate-500">
          {result?.solution
            ? 'AI가 절차를 단계로 나누지 못했습니다. 분석 텍스트를 참고하세요.'
            : '검색 결과가 없습니다.'}
        </p>
      ) : (
        <div className="mt-6 divide-y divide-slate-700/80">
          {steps.map((item) => (
            <article
              key={item.step}
              className="grid grid-cols-[44px_64px_1fr] items-center gap-5 py-5 first:pt-0 last:pb-0"
            >
              <span className="grid h-10 w-10 place-items-center rounded-full bg-blue-600 text-[17px] font-black text-white shadow-[0_0_20px_rgba(37,99,235,0.35)]">
                {item.step}
              </span>
              <span className="grid h-14 w-14 place-items-center rounded-full bg-blue-500/10 text-blue-400">
                <Wrench className="h-7 w-7" />
              </span>
              <div>
                <p className="text-[19px] font-semibold tracking-[-0.04em] text-white">{item.title}</p>
                {item.source && (
                  <p className="mt-1 text-[12px] font-bold text-blue-300/80">출처: {item.source}</p>
                )}
              </div>
            </article>
          ))}
        </div>
      )}
    </Panel>
  );
}
