import { useEffect, useMemo, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

import { Panel } from '../../../../shared/ui/Panel';
import { searchHistoryApi, type SearchHistoryItem } from '../../infra/searchHistory.api';
import { SearchHistoryFilters } from '../filters/SearchHistoryFilters';
import { SearchHistoryTabs } from '../filters/SearchHistoryTabs';
import { ActionLogTable } from '../table/ActionLogTable';
import { SavedDocsTable } from '../table/SavedDocsTable';
import { SearchHistoryPagination } from '../table/SearchHistoryPagination';
import { SearchHistoryTable } from '../table/SearchHistoryTable';

export type HistoryTab = '검색 이력' | '조치 이력' | '저장 문서';

const PAGE_SIZE = 10;

const PATH_TO_TAB: Record<string, HistoryTab> = {
  '/search-history': '검색 이력',
  '/action-history': '조치 이력',
  '/saved-documents': '저장 문서',
};

const TAB_TO_PATH: Record<HistoryTab, string> = {
  '검색 이력': '/search-history',
  '조치 이력': '/action-history',
  '저장 문서': '/saved-documents',
};

export function SearchHistoryPanel() {
  const navigate = useNavigate();
  const location = useLocation();
  const initialTab = PATH_TO_TAB[location.pathname] ?? '검색 이력';
  const [activeTab, setActiveTab] = useState<HistoryTab>(initialTab);
  const [page, setPage] = useState(1);
  const [items, setItems] = useState<SearchHistoryItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    const next = PATH_TO_TAB[location.pathname];
    if (next && next !== activeTab) setActiveTab(next);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [location.pathname]);

  useEffect(() => {
    setPage(1);
  }, [activeTab]);

  const handleTabChange = (tab: HistoryTab) => {
    setActiveTab(tab);
    const target = TAB_TO_PATH[tab];
    if (target && location.pathname !== target) navigate(target);
  };

  useEffect(() => {
    if (activeTab !== '검색 이력') return;

    let cancelled = false;

    setIsLoading(true);
    setErrorMessage(null);

    searchHistoryApi
      .listMine({ limit: 200 })
      .then((data) => {
        if (!cancelled) setItems(data);
      })
      .catch((error) => {
        if (!cancelled) setErrorMessage(error?.message ?? '검색 이력을 불러오지 못했습니다.');
      })
      .finally(() => {
        if (!cancelled) setIsLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [activeTab]);

  const pagedItems = useMemo(() => {
    const start = (page - 1) * PAGE_SIZE;
    return items.slice(start, start + PAGE_SIZE);
  }, [items, page]);

  return (
    <Panel className="p-5 md:p-6">
      <SearchHistoryTabs activeTab={activeTab} onTabChange={handleTabChange} />
      {activeTab === '검색 이력' && (
        <>
          <SearchHistoryFilters />
          <SearchHistoryTable items={pagedItems} isLoading={isLoading} errorMessage={errorMessage} />
          <SearchHistoryPagination currentPage={page} pageSize={PAGE_SIZE} totalItems={items.length} onPageChange={setPage} />
        </>
      )}
      {activeTab === '조치 이력' && <ActionLogTable />}
      {activeTab === '저장 문서' && <SavedDocsTable />}
    </Panel>
  );
}
