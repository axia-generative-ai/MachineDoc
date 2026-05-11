import { useState } from 'react';
import { ChevronRight, FileText } from 'lucide-react';

import { manualApi, type RelatedManual } from '../../infra/manual.api';

type RelatedManualCardProps = {
  manual: RelatedManual;
};

export function RelatedManualCard({ manual }: RelatedManualCardProps) {
  const [isOpening, setIsOpening] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleClick = async () => {
    setIsOpening(true);
    setErrorMessage(null);
    try {
      await manualApi.openPdf(manual.manualId);
    } catch (error) {
      const message = error instanceof Error ? error.message : '매뉴얼을 여는 중 문제가 발생했습니다.';
      setErrorMessage(message);
    } finally {
      setIsOpening(false);
    }
  };

  return (
    <button
      type="button"
      onClick={handleClick}
      className="flex min-h-[132px] w-full items-center gap-5 rounded-2xl border border-slate-700/80 bg-slate-950/35 p-5 text-left shadow-panel backdrop-blur-xl transition hover:-translate-y-1 hover:border-blue-400/50 hover:bg-slate-900/40"
    >
      <div className="grid h-16 w-16 shrink-0 place-items-center rounded-full bg-blue-500/10 text-blue-400">
        <FileText className="h-8 w-8" />
      </div>

      <div className="min-w-0 flex-1">
        <div className="mb-3 flex items-center gap-3">
          <h3 className="truncate text-[19px] font-extrabold tracking-[-0.04em] text-white">{manual.title}</h3>
          <span className="rounded-md bg-blue-500/15 px-2 py-1 text-[13px] font-black text-blue-300">{manual.version}</span>
        </div>
        <div className="flex items-center gap-3 text-[14px] font-bold text-slate-400">
          <span className="rounded-md bg-slate-800/60 px-2 py-1 text-slate-200">{manual.category}</span>
          <span>{isOpening ? 'PDF 여는 중...' : 'PDF 보기 / 다운로드'}</span>
        </div>
        {errorMessage && (
          <p className="mt-2 text-[13px] font-bold text-red-300">{errorMessage}</p>
        )}
      </div>

      <ChevronRight className="h-7 w-7 shrink-0 text-slate-200" />
    </button>
  );
}
