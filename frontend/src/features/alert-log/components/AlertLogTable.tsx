import { RefreshCw, Search } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

import { Panel } from '../../../shared/ui/Panel';
import type { AlertLogItem, ReadStatus } from '../infra/alertLog.api';
import { AlertBadge } from './AlertBadge';

const READ_STATUS_OPTIONS: ReadStatus[] = ['미확인', '확인', '완료'];

function formatTimestamp(iso: string): string {
  if (!iso) return '-';
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return iso;
  return date.toLocaleString('ko-KR', { hour12: false });
}

type Props = {
  items: AlertLogItem[];
  isLoading: boolean;
  errorMessage: string | null;
  busyId: number | null;
  filterLabel: string;
  onReload: () => void;
  onUpdateStatus: (notificationId: number, isRead: ReadStatus) => void;
};

export function AlertLogTable({ items, isLoading, errorMessage, busyId, filterLabel, onReload, onUpdateStatus }: Props) {
  const navigate = useNavigate();

  const handleRowSearch = (item: AlertLogItem) => {
    const code = item.suggestedErrorCode;
    if (!code) return;
    navigate(`/error-search/result?q=${encodeURIComponent(code)}`);
  };

  return (
    <Panel className="overflow-x-auto px-5 py-4">
      <div className="mb-4 flex items-center justify-end gap-3 px-2 text-[13px] font-bold text-slate-400">
        <span>총 {items.length}건</span>
        <button
          type="button"
          onClick={onReload}
          disabled={isLoading}
          className="grid h-9 w-9 place-items-center rounded-lg border border-slate-700 text-slate-300 transition hover:border-blue-400/60 hover:text-blue-300 disabled:opacity-50"
          aria-label="새로고침"
        >
          <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {errorMessage && (
        <p className="mb-4 rounded-lg border border-red-500/40 bg-red-500/10 px-4 py-3 text-[14px] font-bold text-red-300">
          {errorMessage}
        </p>
      )}

      <div className="min-w-[1180px]">
        <div className="grid grid-cols-[180px_120px_180px_1fr_140px_140px_120px] items-center border-b border-slate-700/80 px-7 py-4 text-[15px] font-black text-slate-400">
          <span>시각</span>
          <span className="text-center">등급</span>
          <span className="text-center">설비</span>
          <span>내용</span>
          <span className="text-center">상태</span>
          <span className="text-center">상태 변경</span>
          <span className="text-right">검색</span>
        </div>

        {isLoading ? (
          <p className="px-7 py-12 text-center text-[14px] font-bold text-slate-400">불러오는 중...</p>
        ) : items.length === 0 ? (
          <p className="px-7 py-12 text-center text-[14px] font-bold text-slate-500">
            {filterLabel === '전체' ? '알림 이력이 없습니다.' : `'${filterLabel}' 등급 알림이 없습니다.`}
          </p>
        ) : (
          <div className="divide-y divide-slate-800/90">
            {items.map((row) => {
              const canSearch = !!row.suggestedErrorCode;
              return (
                <article
                  key={row.notificationId}
                  onClick={() => canSearch && handleRowSearch(row)}
                  className={`grid grid-cols-[180px_120px_180px_1fr_140px_140px_120px] items-center px-7 py-4 text-[15px] font-semibold text-slate-200 transition ${canSearch ? 'cursor-pointer hover:bg-blue-500/[0.05]' : ''}`}
                  title={canSearch ? `클릭 시 ${row.suggestedErrorCode} 검색` : ''}
                >
                  <span className="text-slate-300">{formatTimestamp(row.occurredAt)}</span>
                  <span className="text-center">
                    <AlertBadge type="severity" value={row.level} />
                  </span>
                  <span className="text-center">
                    <span className="font-mono text-blue-300">{row.equipmentCode}</span>
                    <span className="ml-2 text-[12px] text-slate-500">{row.location}</span>
                  </span>
                  <span className="truncate text-slate-300" title={row.message}>
                    {row.message}
                  </span>
                  <span className="text-center">
                    <AlertBadge type="status" value={row.isRead} />
                  </span>
                  <div className="flex justify-center" onClick={(event) => event.stopPropagation()}>
                    <select
                      value={row.isRead}
                      onChange={(event) => onUpdateStatus(row.notificationId, event.target.value as ReadStatus)}
                      disabled={busyId === row.notificationId}
                      className="h-9 rounded-lg border border-slate-700 bg-slate-950/50 px-2 text-[13px] font-bold text-white outline-none focus:border-blue-400/70 disabled:opacity-50"
                    >
                      {READ_STATUS_OPTIONS.map((option) => (
                        <option key={option} value={option} className="bg-slate-950 text-white">
                          {option}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div className="flex justify-end" onClick={(event) => event.stopPropagation()}>
                    <button
                      type="button"
                      onClick={() => handleRowSearch(row)}
                      disabled={!canSearch}
                      className="inline-flex h-9 items-center gap-1 rounded-lg border border-blue-400/60 bg-blue-500/10 px-3 text-[13px] font-black text-blue-300 transition hover:bg-blue-500/20 disabled:cursor-not-allowed disabled:opacity-40"
                      title={canSearch ? `${row.suggestedErrorCode} 검색` : '연결된 오류 코드 없음'}
                    >
                      <Search className="h-4 w-4" />
                      {row.suggestedErrorCode ?? '-'}
                    </button>
                  </div>
                </article>
              );
            })}
          </div>
        )}
      </div>
    </Panel>
  );
}
