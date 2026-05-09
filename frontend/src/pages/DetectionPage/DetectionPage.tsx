import { useState } from 'react';

import { AnalysisResultPanel } from '../../features/detection/components/AnalysisResultPanel';
import { DetectionHeader } from '../../features/detection/components/DetectionHeader';
import { VirtualLogInput } from '../../features/detection/components/VirtualLogInput';
import type { EquipmentLogResult } from '../../features/detection/infra/detection.api';

export function DetectionPage() {
  const [result, setResult] = useState<EquipmentLogResult | null>(null);

  return (
    <div className="mx-auto max-w-[1640px]">
      <DetectionHeader />

      <div className="grid gap-5 lg:grid-cols-12">
        <VirtualLogInput onResult={setResult} />
        <AnalysisResultPanel result={result} />
      </div>
    </div>
  );
}
