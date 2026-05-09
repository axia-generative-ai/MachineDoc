import { useState } from 'react';

import { AlertLogHeader } from '../../features/alert-log/components/AlertLogHeader';
import { AlertLogTable } from '../../features/alert-log/components/AlertLogTable';
import { useAlertLog } from '../../features/alert-log/hooks/useAlertLog';
import { alertFilters } from '../../features/alert-log/model/alertLogData';

export function AlertLogPage() {
  const [filter, setFilter] = useState<(typeof alertFilters)[number]>('전체');
  const { filtered, isLoading, errorMessage, busyId, load, updateStatus } = useAlertLog(filter);

  return (
    <div className="mx-auto max-w-[1640px]">
      <AlertLogHeader selectedFilter={filter} onFilterChange={setFilter} items={filtered} />
      <AlertLogTable
        items={filtered}
        isLoading={isLoading}
        errorMessage={errorMessage}
        busyId={busyId}
        filterLabel={filter}
        onReload={() => void load()}
        onUpdateStatus={(id, status) => void updateStatus(id, status)}
      />
    </div>
  );
}
