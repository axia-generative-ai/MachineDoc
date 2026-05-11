import { Bot, CheckCircle2, Wrench } from 'lucide-react';

import type { ErrorSearchResult } from '../../model/errorSearch.types';
import { Panel } from '../../../../shared/ui/Panel';

type ErrorSearchAiSummaryProps = {
  result: ErrorSearchResult;
};

// LLM이 [섹션 헤더]를 본문에 섞어 출력하는데 그대로 두면 한 줄로 흘러가서 가독성이 나쁨.
// 섹션 헤더는 굵은 라벨, 내용은 줄바꿈 보존, (출처: ...)은 별도 라벨로 분리.
const SECTION_RE = /^\s*\[(?<title>[^\]]+)\]\s*$/;
const SOURCE_RE = /\(출처:\s*([^)]+)\)/g;

type Block =
  | { kind: 'heading'; title: string }
  | { kind: 'text'; text: string; sources: string[] };

function parseBlocks(raw: string): Block[] {
  const blocks: Block[] = [];
  const lines = raw.split(/\r?\n/);
  let buffer: string[] = [];

  const flushBuffer = () => {
    if (buffer.length === 0) return;
    const joined = buffer.join('\n').trim();
    if (!joined) {
      buffer = [];
      return;
    }
    const sources: string[] = [];
    const cleaned = joined.replace(SOURCE_RE, (_, body: string) => {
      sources.push(body.trim());
      return '';
    });
    blocks.push({
      kind: 'text',
      text: cleaned.replace(/\s+\n/g, '\n').replace(/[ \t]+$/gm, '').trim(),
      sources,
    });
    buffer = [];
  };

  for (const line of lines) {
    const heading = SECTION_RE.exec(line);
    if (heading) {
      flushBuffer();
      blocks.push({ kind: 'heading', title: heading.groups!.title.trim() });
      continue;
    }
    buffer.push(line);
  }
  flushBuffer();
  return blocks;
}

function FormattedAnalysis({ text }: { text: string }) {
  const blocks = parseBlocks(text);
  if (blocks.length === 0) {
    return <p className="whitespace-pre-line text-[15px] font-semibold leading-7 text-slate-300">{text}</p>;
  }
  return (
    <div className="space-y-3 text-[15px] leading-7 text-slate-300">
      {blocks.map((b, i) =>
        b.kind === 'heading' ? (
          <p key={i} className="mt-2 text-[13px] font-black tracking-[0.12em] text-blue-300">
            {b.title.toUpperCase()}
          </p>
        ) : (
          <div key={i}>
            <p className="whitespace-pre-line font-semibold">{b.text}</p>
            {b.sources.length > 0 && (
              <ul className="mt-2 flex flex-wrap gap-1.5">
                {b.sources.map((s, idx) => (
                  <li
                    key={idx}
                    className="rounded-md bg-blue-500/10 px-2 py-0.5 text-[12px] font-bold text-blue-300/90"
                  >
                    출처: {s}
                  </li>
                ))}
              </ul>
            )}
          </div>
        ),
      )}
    </div>
  );
}

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
            <FormattedAnalysis text={result.analysis} />
          </article>

          <article className="rounded-xl border border-slate-700/80 bg-slate-950/35 p-4">
            <div className="mb-3 flex items-center gap-2 text-orange-300">
              <Wrench className="h-5 w-5" />
              <h3 className="text-[16px] font-black">권장 조치</h3>
            </div>
            <FormattedAnalysis text={result.solution} />
          </article>
        </div>
      </div>
    </Panel>
  );
}
