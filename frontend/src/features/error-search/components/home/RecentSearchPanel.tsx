import { useEffect, useState } from 'react';
import { Clock3 } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

import { Panel } from '../../../../shared/ui/Panel';
import { searchHistoryApi, type SearchHistoryItem } from '../../../search-history/infra/searchHistory.api';

function formatRelative(iso: string): string {
  if (!iso) return '';
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return iso;
  const diffMs = Date.now() - date.getTime();
  const diffMin = Math.floor(diffMs / 60_000);
  if (diffMin < 1) return '방금 전';
  if (diffMin < 60) return `${diffMin}분 전`;
  const diffH = Math.floor(diffMin / 60);
  if (diffH < 24) return `${diffH}시간 전`;
  const diffD = Math.floor(diffH / 24);
  return `${diffD}일 전`;
}

export function RecentSearchPanel() {
  const navigate = useNavigate();
  const [items, setItems] = useState<SearchHistoryItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    searchHistoryApi
      .listMine({ limit: 5 })
      .then((data) => {
        if (!cancelled) setItems(data);
      })
      .catch(() => {
        if (!cancelled) setItems([]);
      })
      .finally(() => {
        if (!cancelled) setIsLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <Panel className="p-5">
      <div className="mb-4 flex items-center gap-3">
        <Clock3 className="h-6 w-6 text-blue-400" />
        <h2 className="text-[22px] font-black tracking-[-0.05em] text-white">최근 검색</h2>
      </div>

      {isLoading ? (
        <p className="py-6 text-center text-[14px] font-bold text-slate-400">불러오는 중...</p>
      ) : items.length === 0 ? (
        <p className="py-6 text-center text-[14px] font-bold text-slate-500">최근 검색 이력이 없습니다.</p>
      ) : (
        <div className="divide-y divide-slate-800/90">
          {items.map((item) => (
            <button
              key={item.historyId}
              type="button"
              onClick={() => navigate(`/error-search/result?q=${encodeURIComponent(item.query)}`)}
              className="flex w-full items-center justify-between gap-4 py-4 text-left transition hover:text-blue-300"
            >
              <span className="truncate font-mono text-[17px] font-bold text-slate-200">{item.query}</span>
              <span className="shrink-0 text-[14px] font-semibold text-slate-500">{formatRelative(item.createdAt)}</span>
            </button>
          ))}
        </div>
      )}
    </Panel>
  );
}
