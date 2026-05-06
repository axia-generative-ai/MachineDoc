import { AlertLogHeader } from '../../features/alert-log/components/AlertLogHeader';
import { AlertLogTable } from '../../features/alert-log/components/AlertLogTable';

export function AlertLogPage() {
  return (
    <div className="mx-auto max-w-[1640px]">
      <AlertLogHeader />
      <AlertLogTable />
    </div>
  );
}
