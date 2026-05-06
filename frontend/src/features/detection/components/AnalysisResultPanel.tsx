import { analysisResults } from '../model/detectionData';
import { Panel } from '../../../shared/ui/Panel';
import { AnalysisResultCard } from './AnalysisResultCard';

export function AnalysisResultPanel() {
  return (
    <Panel className="p-5 lg:col-span-6 xl:col-span-6">
      <h2 className="text-[22px] font-black tracking-[-0.05em] text-white">분석 결과</h2>

      <div className="mt-5 space-y-4">
        {analysisResults.map((item) => (
          <AnalysisResultCard key={item.label} item={item} />
        ))}
      </div>

      <p className="mt-6 text-center text-[16px] font-semibold tracking-[-0.04em] text-slate-500">룰 1차 + LLM 2차 분석</p>
    </Panel>
  );
}
