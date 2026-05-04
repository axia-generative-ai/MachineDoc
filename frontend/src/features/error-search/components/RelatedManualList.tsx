import { relatedManuals } from '../model/errorSearchData';
import { RelatedManualCard } from './RelatedManualCard';

export function RelatedManualList() {
  return (
    <div className="grid gap-5 lg:grid-cols-3">
      {relatedManuals.map((manual) => (
        <RelatedManualCard key={manual.title} manual={manual} />
      ))}
    </div>
  );
}
