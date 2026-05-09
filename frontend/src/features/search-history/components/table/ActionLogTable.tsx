import { useEffect, useState } from 'react';
import { CheckCircle2, Clock3, Search, Wrench, XCircle } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

import { actionLogApi, type ActionLogItem, type ActionStatusValue } from '../../infra/actionLog.api';

const statusStyles: Record<ActionStatusValue, { className: string; icon: typeof CheckCircle2 }> = {
  완료: { className: 'border-emerald-400/40 bg-emerald-500/10 text-emerald-300', icon: CheckCircle2 },
  '부분 완료': { className: 'border-amber-400/40 bg-amber-500/10 text-amber-300', icon: Wrench },
  '추가 점검 필요': { className: 'border-blue-400/40 bg-blue-500/10 text-blue-300', icon: Clock3 },
  '조치 불가': { className: 'border-red-400/40 bg-red-500/10 text-red-300', icon: XCircle },
};

function formatTimestamp(iso: string): string {
  if (!iso) return '-';
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return iso;
  return date.toLocaleString('ko-KR', { hour12: false });
}

export function ActionLogTable() {
  const navigate = useNavigate();
  const [items, setItems] = useState<ActionLogItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setIsLoading(true);
    setErrorMessage(null);
    actionLogApi
      .listMine(50)
      .then((data) => {
        if (!cancelled) setItems(data);
      })
      .catch((error) => {
        if (!cancelled) setErrorMessage(error?.message ?? '조치 이력을 불러오지 못했습니다.');
      })
      .finally(() => {
        if (!cancelled) setIsLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <>
    <div className="mt-5 mb-4 flex items-center justify-between rounded-xl border border-slate-700/80 bg-slate-900/30 px-5 py-3">
      <p className="text-[13px] font-bold text-slate-400">
        조치 이력은 <span className="text-blue-300">오류코드 검색 결과 화면</span>에서 "조치 결과 입력" 버튼으로 등록됩니다.
      </p>
      <button
        type="button"
        onClick={() => navigate('/error-search')}
        className="inline-flex h-9 items-center gap-2 rounded-lg border border-blue-400/60 bg-blue-500/10 px-3 text-[13px] font-black text-blue-300 transition hover:bg-blue-500/20"
      >
        <Search className="h-4 w-4" />
        검색하러 가기
      </button>
    </div>
    <div className="overflow-hidden rounded-2xl border border-slate-700/80 bg-slate-950/25">
      <div className="grid grid-cols-[180px_1fr_1.6fr_120px_140px] border-b border-slate-700/80 bg-slate-900/60 px-6 py-4 text-[14px] font-black text-slate-400 max-lg:hidden">
        <span>조치 일시</span>
        <span>검색 코드</span>
        <span>코멘트</span>
        <span>소요 시간</span>
        <span className="text-right">상태</span>
      </div>

      {isLoading ? (
        <p className="px-6 py-10 text-center text-[14px] font-bold text-slate-400">불러오는 중...</p>
      ) : errorMessage ? (
        <p className="px-6 py-10 text-center text-[14px] font-bold text-red-300">{errorMessage}</p>
      ) : items.length === 0 ? (
        <p className="px-6 py-10 text-center text-[14px] font-bold text-slate-500">
          조치 이력이 없습니다. 검색 결과 화면에서 "조치 결과 입력"을 통해 등록할 수 있습니다.
        </p>
      ) : (
        <div className="divide-y divide-slate-800/90">
          {items.map((item) => {
            const style = statusStyles[item.actionStatus] ?? statusStyles['추가 점검 필요'];
            const StatusIcon = style.icon;
            return (
              <article
                key={item.actionLogId}
                className="grid gap-3 px-5 py-5 transition hover:bg-blue-500/[0.04] lg:grid-cols-[180px_1fr_1.6fr_120px_140px] lg:items-center lg:px-6"
              >
                <div>
                  <p className="text-[13px] font-bold text-slate-500 lg:hidden">조치 일시</p>
                  <p className="text-[14px] font-semibold text-slate-300">{formatTimestamp(item.createdAt)}</p>
                </div>
                <div>
                  <p className="text-[13px] font-bold text-slate-500 lg:hidden">검색 코드</p>
                  <p className="font-mono text-[16px] font-black tracking-[-0.04em] text-white">{item.query}</p>
                </div>
                <div className="min-w-0">
                  <p className="text-[13px] font-bold text-slate-500 lg:hidden">코멘트</p>
                  <p className="truncate text-[14px] font-semibold text-slate-300" title={item.comment ?? ''}>
                    {item.comment || '-'}
                  </p>
                </div>
                <div>
                  <p className="text-[13px] font-bold text-slate-500 lg:hidden">소요 시간</p>
                  <p className="text-[14px] font-semibold text-slate-300">
                    {item.duration != null ? `${item.duration}분` : '-'}
                  </p>
                </div>
                <div className="flex lg:justify-end">
                  <span className={`inline-flex h-9 items-center gap-2 rounded-lg border px-3 text-[14px] font-black ${style.className}`}>
                    <StatusIcon className="h-4 w-4" />
                    {item.actionStatus}
                  </span>
                </div>
              </article>
            );
          })}
        </div>
      )}
    </div>
    </>
  );
}
