import { useEffect, useState } from 'react';
import { ExternalLink, FileText } from 'lucide-react';

import type { ErrorSearchResult, ManualCitation } from '../../model/errorSearch.types';
import { manualApi } from '../../infra/manual.api';
import { Panel } from '../../../../shared/ui/Panel';

type Props = {
  result: ErrorSearchResult | null;
};

export function ManualPreview({ result }: Props) {
  const citations = result?.citations ?? [];
  const primary = citations[0];
  const [active, setActive] = useState<ManualCitation | null>(null);
  const [pdfUrl, setPdfUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 첫 인용을 기본 활성화. 결과가 바뀌면 동기화.
  useEffect(() => {
    setActive(primary ?? null);
  }, [primary?.manualId, primary?.filename, primary?.page]);

  useEffect(() => {
    if (!active || active.manualId == null) {
      setPdfUrl(null);
      return;
    }
    let revoke: (() => void) | null = null;
    let cancelled = false;
    setLoading(true);
    setError(null);
    manualApi
      .fetchPdfUrl(active.manualId, active.page)
      .then((res) => {
        if (cancelled) {
          res.revoke();
          return;
        }
        revoke = res.revoke;
        setPdfUrl(res.url);
      })
      .catch((err) => {
        if (!cancelled) setError(err instanceof Error ? err.message : '매뉴얼을 불러오지 못했습니다.');
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
      revoke?.();
    };
  }, [active?.manualId, active?.page]);

  return (
    <Panel className="min-h-[455px] p-6 lg:col-span-7">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-[24px] font-extrabold tracking-[-0.04em] text-white">매뉴얼 인용</h2>
        {primary && (
          <span className="text-[14px] font-bold text-slate-400">출처 {citations.length}건</span>
        )}
      </div>

      {!result ? (
        <p className="rounded-xl border border-slate-700/80 bg-slate-950/20 px-5 py-10 text-center text-[14px] font-bold text-slate-500">
          검색 결과가 없습니다.
        </p>
      ) : citations.length === 0 ? (
        <div className="rounded-xl border border-slate-700/80 bg-slate-950/20 px-5 py-10 text-center">
          <FileText className="mx-auto h-10 w-10 text-slate-500" />
          <p className="mt-4 text-[15px] font-bold text-slate-400">매뉴얼 출처가 없습니다.</p>
          <p className="mt-2 text-[13px] font-medium text-slate-500">
            AI가 매뉴얼에서 직접 인용하지 않은 일반 답변입니다.
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          <div className="flex flex-wrap items-center justify-between gap-2 rounded-lg border border-blue-400/30 bg-blue-500/5 px-4 py-2">
            <div className="flex min-w-0 items-center gap-2">
              <FileText className="h-4 w-4 shrink-0 text-blue-400" />
              <span className="truncate text-[14px] font-bold text-white" title={active?.filename ?? primary.filename}>
                {active?.filename ?? primary.filename}
              </span>
              <span className="ml-2 shrink-0 rounded-md bg-blue-500/20 px-2 py-0.5 text-[12px] font-black text-blue-200">
                p. {active?.page ?? primary.page}
              </span>
            </div>
            {active?.manualId != null && (
              <button
                type="button"
                onClick={() => manualApi.openPdf(active.manualId!, active.page)}
                className="flex shrink-0 items-center gap-1 rounded-md border border-slate-600 px-2 py-1 text-[12px] font-bold text-slate-300 transition hover:border-blue-400 hover:text-blue-300"
              >
                <ExternalLink className="h-3.5 w-3.5" />새 탭에서 열기
              </button>
            )}
          </div>

          <div className="relative h-[520px] overflow-hidden rounded-xl border border-slate-700/80 bg-slate-950">
            {loading && (
              <div className="absolute inset-0 grid place-items-center text-[13px] font-bold text-slate-400">
                매뉴얼 불러오는 중...
              </div>
            )}
            {error && !loading && (
              <div className="absolute inset-0 grid place-items-center px-4 text-center text-[13px] font-bold text-red-300">
                {error}
              </div>
            )}
            {!loading && !error && active?.manualId == null && (
              <div className="absolute inset-0 grid place-items-center px-4 text-center text-[13px] font-bold text-slate-400">
                연결된 매뉴얼 파일을 찾지 못했습니다.
              </div>
            )}
            {pdfUrl && !loading && !error && (
              <iframe
                key={pdfUrl}
                src={pdfUrl}
                title={active?.filename ?? '매뉴얼 미리보기'}
                className="h-full w-full"
              />
            )}
          </div>

          {citations.length > 1 && (
            <div>
              <p className="mb-2 text-[12px] font-bold text-slate-400">추가 인용 ({citations.length - 1})</p>
              <ul className="flex flex-wrap gap-2">
                {citations.map((cite) => {
                  const isActive =
                    active?.filename === cite.filename && active?.page === cite.page && active?.manualId === cite.manualId;
                  return (
                    <li key={`${cite.filename}-${cite.page}`}>
                      <button
                        type="button"
                        onClick={() => setActive(cite)}
                        disabled={cite.manualId == null}
                        className={`flex items-center gap-2 rounded-lg border px-3 py-1.5 text-[12px] font-bold transition disabled:cursor-not-allowed disabled:opacity-50 ${
                          isActive
                            ? 'border-blue-400 bg-blue-500/15 text-blue-200'
                            : 'border-slate-700 bg-slate-950/40 text-slate-300 hover:border-blue-400/60 hover:text-blue-300'
                        }`}
                        title={cite.manualId == null ? '연결된 매뉴얼 파일을 찾지 못했습니다' : `${cite.filename} p.${cite.page}`}
                      >
                        <span className="max-w-[180px] truncate">{cite.filename}</span>
                        <span className="font-mono">p.{cite.page}</span>
                      </button>
                    </li>
                  );
                })}
              </ul>
            </div>
          )}
        </div>
      )}
    </Panel>
  );
}
