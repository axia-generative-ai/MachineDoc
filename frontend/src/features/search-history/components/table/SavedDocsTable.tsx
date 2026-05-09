import { useEffect, useState } from 'react';
import { Download, FileText } from 'lucide-react';

import { manualApi, type RelatedManual } from '../../../error-search/infra/manual.api';
import { SearchHistoryPagination } from './SearchHistoryPagination';

const PAGE_SIZE = 10;

function formatTimestamp(iso: string): string {
  if (!iso) return '-';
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return iso;
  return date.toLocaleString('ko-KR', { hour12: false });
}

export function SavedDocsTable() {
  const [items, setItems] = useState<RelatedManual[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [openingId, setOpeningId] = useState<number | null>(null);
  const [page, setPage] = useState(1);

  useEffect(() => {
    let cancelled = false;
    setIsLoading(true);
    setErrorMessage(null);
    manualApi
      .listMine()
      .then((data) => {
        if (!cancelled) setItems(data);
      })
      .catch((error) => {
        if (!cancelled) setErrorMessage(error?.message ?? '저장한 문서를 불러오지 못했습니다.');
      })
      .finally(() => {
        if (!cancelled) setIsLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const handleOpen = async (manualId: number) => {
    setOpeningId(manualId);
    try {
      await manualApi.openPdf(manualId);
    } finally {
      setOpeningId(null);
    }
  };

  const start = (page - 1) * PAGE_SIZE;
  const pagedItems = items.slice(start, start + PAGE_SIZE);

  return (
    <>
    <div className="mt-5 overflow-hidden rounded-2xl border border-slate-700/80 bg-slate-950/25">
      <div className="grid grid-cols-[180px_1fr_120px_120px_140px] border-b border-slate-700/80 bg-slate-900/60 px-6 py-4 text-[14px] font-black text-slate-400 max-lg:hidden">
        <span>저장 일시</span>
        <span>제목</span>
        <span>카테고리</span>
        <span>버전</span>
        <span className="text-right">PDF</span>
      </div>

      {isLoading ? (
        <p className="px-6 py-10 text-center text-[14px] font-bold text-slate-400">불러오는 중...</p>
      ) : errorMessage ? (
        <p className="px-6 py-10 text-center text-[14px] font-bold text-red-300">{errorMessage}</p>
      ) : items.length === 0 ? (
        <p className="px-6 py-10 text-center text-[14px] font-bold text-slate-500">
          저장한 문서가 없습니다. 관리자 페이지에서 매뉴얼을 등록하면 여기 표시됩니다.
        </p>
      ) : (
        <div className="divide-y divide-slate-800/90">
          {pagedItems.map((item) => (
            <article
              key={item.manualId}
              className="grid gap-3 px-5 py-5 transition hover:bg-blue-500/[0.04] lg:grid-cols-[180px_1fr_120px_120px_140px] lg:items-center lg:px-6"
            >
              <div>
                <p className="text-[13px] font-bold text-slate-500 lg:hidden">저장 일시</p>
                <p className="text-[14px] font-semibold text-slate-300">{formatTimestamp(item.savedAt)}</p>
              </div>
              <div className="flex min-w-0 items-center gap-3">
                <FileText className="h-5 w-5 shrink-0 text-blue-400" />
                <p className="truncate text-[16px] font-bold text-white" title={item.title}>
                  {item.title}
                </p>
              </div>
              <div>
                <p className="text-[13px] font-bold text-slate-500 lg:hidden">카테고리</p>
                <span className="inline-flex h-7 items-center rounded-md bg-slate-800/60 px-2 text-[13px] font-black text-slate-200">
                  {item.category}
                </span>
              </div>
              <div>
                <p className="text-[13px] font-bold text-slate-500 lg:hidden">버전</p>
                <span className="font-mono text-[14px] font-bold text-blue-300">{item.version}</span>
              </div>
              <div className="flex lg:justify-end">
                <button
                  type="button"
                  onClick={() => void handleOpen(item.manualId)}
                  disabled={openingId === item.manualId}
                  className="inline-flex h-9 items-center gap-2 rounded-lg border border-blue-400/60 bg-blue-500/10 px-3 text-[13px] font-black text-blue-300 transition hover:bg-blue-500/20 disabled:opacity-60"
                >
                  <Download className="h-4 w-4" />
                  {openingId === item.manualId ? '열림 중...' : 'PDF 보기'}
                </button>
              </div>
            </article>
          ))}
        </div>
      )}
    </div>
    <SearchHistoryPagination currentPage={page} pageSize={PAGE_SIZE} totalItems={items.length} onPageChange={setPage} />
    </>
  );
}
