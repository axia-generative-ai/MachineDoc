import type { ManualSummary } from '../../infra/manual.api';
import { RelatedManualCard } from './RelatedManualCard';

type RelatedManualListProps = {
  manuals: ManualSummary[];
  selectedManualId?: number;
  isLoading: boolean;
  errorMessage: string | null;
  onSelect: (manual: ManualSummary) => void;
};

export function RelatedManualList({ manuals, selectedManualId, isLoading, errorMessage, onSelect }: RelatedManualListProps) {
  if (isLoading) {
    return <div className="rounded-lg border border-slate-800 bg-slate-950/30 p-5 text-[15px] font-semibold text-slate-300">관련 매뉴얼을 불러오는 중입니다.</div>;
  }

  if (errorMessage) {
    return <div className="rounded-lg border border-red-500/30 bg-red-950/20 p-5 text-[15px] font-semibold text-red-200">{errorMessage}</div>;
  }

  if (manuals.length === 0) {
    return <div className="rounded-lg border border-slate-800 bg-slate-950/30 p-5 text-[15px] font-semibold text-slate-400">등록된 매뉴얼이 없습니다.</div>;
  }

  return (
    <div className="grid gap-5 lg:grid-cols-3">
      {manuals.map((manual) => (
        <RelatedManualCard key={manual.manual_id} manual={manual} isSelected={manual.manual_id === selectedManualId} onSelect={onSelect} />
      ))}
    </div>
  );
}
