import { SearchHistoryHeader, SearchHistoryPanel } from '../../features/search-history/components';

export function SearchHistoryPage() {
  return (
    <div className="mx-auto max-w-[1640px]">
      <SearchHistoryHeader />
      <SearchHistoryPanel />
    </div>
  );
}
