import { ErrorCodeMappingPanel } from './ErrorCodeMappingPanel';
import { ManualSettingsPanel } from './ManualSettingsPanel';

export function AdminManualRegistration() {
  return (
    <div className="grid gap-6 lg:grid-cols-12">
      <ManualSettingsPanel />
      <ErrorCodeMappingPanel />
    </div>
  );
}
