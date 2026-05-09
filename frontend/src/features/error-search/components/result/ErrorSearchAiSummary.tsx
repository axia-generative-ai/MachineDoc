import { Bot, CheckCircle2, Wrench } from 'lucide-react';

import { Panel } from '../../../../shared/ui/Panel';
import type { ErrorSearchResult } from '../../model/errorSearch.types';

type ErrorSearchAiSummaryProps = {
  result: ErrorSearchResult;
};

type ReadableSection = {
  title?: string;
  content: string;
};

type ReadableItem = {
  text: string;
  source?: string;
};

function normalizeText(text: string) {
  return text.replace(/\s+/g, ' ').trim();
}

function splitSections(text: string): ReadableSection[] {
  const normalized = normalizeText(text);
  const matches = [...normalized.matchAll(/\[([^\]]+)\]\s*/g)];

  if (matches.length === 0) {
    return [{ content: normalized }];
  }

  return matches.map((match, index) => {
    const nextMatch = matches[index + 1];
    const contentStart = match.index! + match[0].length;
    const contentEnd = nextMatch?.index ?? normalized.length;

    return {
      title: match[1],
      content: normalized.slice(contentStart, contentEnd).trim(),
    };
  });
}

function splitNumberedItems(text: string) {
  const items = normalizeText(text)
    .split(/(?=\d+\.\s)/)
    .map((item) => item.trim())
    .filter(Boolean)
    .map((item) => item.replace(/^\d+\.\s*/, '').trim());

  return items.length > 1 ? items : [];
}

function moveLeadingSource(text: string): ReadableItem {
  const sourceMatch = text.match(/^\((출처:[^)]+)\)\s*(.*)$/);

  if (!sourceMatch) {
    return { text };
  }

  return {
    text: sourceMatch[2].trim(),
    source: sourceMatch[1].trim(),
  };
}

function splitSentences(text: string) {
  return normalizeText(text)
    .split(/(?<=\.|다\.|요\.|함\.|됨\.)\s+/)
    .map((item) => item.trim())
    .filter(Boolean);
}

function ReadableAiText({ text }: { text: string }) {
  const sections = splitSections(text);

  return (
    <div className="space-y-4 text-[14px] font-medium leading-7 text-slate-200">
      {sections.map((section, sectionIndex) => {
        const numberedItems = splitNumberedItems(section.content);
        const sentences = numberedItems.length > 0 ? [] : splitSentences(section.content);

        return (
          <section key={`${section.title ?? 'section'}-${sectionIndex}`} className="space-y-3">
            {section.title && (
              <h4 className="inline-flex rounded-md bg-slate-800/90 px-2.5 py-1 text-[13px] font-black text-slate-100">
                {section.title}
              </h4>
            )}

            {numberedItems.length > 0 ? (
              <ol className="space-y-3">
                {numberedItems.map((item, itemIndex) => {
                  const readableItem = moveLeadingSource(item);

                  return (
                    <li key={`${itemIndex}-${item.slice(0, 16)}`} className="grid grid-cols-[28px_1fr] gap-3">
                      <span className="mt-1 grid h-6 w-6 place-items-center rounded-full bg-blue-500/15 text-[12px] font-black text-blue-200">
                        {itemIndex + 1}
                      </span>
                      <span>
                        {readableItem.text}
                        {readableItem.source && (
                          <span className="ml-2 inline-flex rounded bg-slate-800/80 px-2 py-0.5 text-[12px] font-bold text-slate-400">
                            {readableItem.source}
                          </span>
                        )}
                      </span>
                    </li>
                  );
                })}
              </ol>
            ) : (
              <div className="space-y-2">
                {sentences.map((sentence, sentenceIndex) => {
                  const readableItem = moveLeadingSource(sentence);

                  return (
                    <p key={`${sentenceIndex}-${sentence.slice(0, 16)}`}>
                      {readableItem.text}
                      {readableItem.source && (
                        <span className="ml-2 inline-flex rounded bg-slate-800/80 px-2 py-0.5 text-[12px] font-bold text-slate-400">
                          {readableItem.source}
                        </span>
                      )}
                    </p>
                  );
                })}
              </div>
            )}
          </section>
        );
      })}
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
            <h2 className="mt-1 text-[22px] font-black text-white">{result.keyword}</h2>
            <p className="mt-1 text-[14px] font-semibold text-emerald-300">{result.status}</p>
          </div>
        </div>

        <div className="grid flex-1 gap-4 xl:grid-cols-2">
          <article className="rounded-xl border border-slate-700/80 bg-slate-950/35 p-5">
            <div className="mb-4 flex items-center gap-2 text-blue-300">
              <CheckCircle2 className="h-5 w-5" />
              <h3 className="text-[16px] font-black">분석 결과</h3>
            </div>
            <ReadableAiText text={result.analysis} />
          </article>

          <article className="rounded-xl border border-slate-700/80 bg-slate-950/35 p-5">
            <div className="mb-4 flex items-center gap-2 text-orange-300">
              <Wrench className="h-5 w-5" />
              <h3 className="text-[16px] font-black">권장 조치</h3>
            </div>
            <ReadableAiText text={result.solution} />
          </article>
        </div>
      </div>
    </Panel>
  );
}
