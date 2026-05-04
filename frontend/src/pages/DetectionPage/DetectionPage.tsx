import { AnalysisResultPanel } from '../../features/detection/components/AnalysisResultPanel';
import { DetectionHeader } from '../../features/detection/components/DetectionHeader';
import { VirtualLogInput } from '../../features/detection/components/VirtualLogInput';

export function DetectionPage() {
  return (
    <div className="mx-auto max-w-[1640px]">
      <DetectionHeader />

      <div className="grid gap-5 lg:grid-cols-12">
        <VirtualLogInput />
        <AnalysisResultPanel />
      </div>
    </div>
  );
}
