import { Panel } from '../../../../shared/ui/Panel';
import { SearchHistoryFilters } from '../filters/SearchHistoryFilters';
import { SearchHistoryPagination } from '../table/SearchHistoryPagination';
import { SearchHistoryTable } from '../table/SearchHistoryTable';
import { SearchHistoryTabs } from '../filters/SearchHistoryTabs';

export function SearchHistoryPanel() {
  return (
    <Panel className="p-5 md:p-6">
      <SearchHistoryTabs />
      <SearchHistoryFilters />
      <SearchHistoryTable />
      <SearchHistoryPagination />
    </Panel>
  );
}

