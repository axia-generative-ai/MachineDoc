import { useEffect, useState } from 'react';

import { AlertLogHeader } from '../../features/alert-log/components/AlertLogHeader';
import { AlertLogTable } from '../../features/alert-log/components/AlertLogTable';
import { ALERT_LOG_PAGE_SIZE, useAlertLog } from '../../features/alert-log/hooks/useAlertLog';
import { alertFilters } from '../../features/alert-log/model/alertLogData';

export function AlertLogPage() {
  const [filter, setFilter] = useState<(typeof alertFilters)[number]>(alertFilters[0]);
  const [page, setPage] = useState(1);
  const { filtered, pagedItems, isLoading, errorMessage, busyId, load, updateStatus } = useAlertLog(filter, page);

  useEffect(() => {
    setPage(1);
  }, [filter]);

  return (
    <div className="mx-auto max-w-[1640px]">
      <AlertLogHeader selectedFilter={filter} onFilterChange={setFilter} items={filtered} />
      <AlertLogTable
        items={pagedItems}
        totalItems={filtered.length}
        currentPage={page}
        pageSize={ALERT_LOG_PAGE_SIZE}
        isLoading={isLoading}
        errorMessage={errorMessage}
        busyId={busyId}
        filterLabel={filter}
        onReload={() => void load()}
        onPageChange={setPage}
        onUpdateStatus={(id, status) => void updateStatus(id, status)}
      />
    </div>
  );
}
