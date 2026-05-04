import { ActionProcedure } from '../../features/error-search/components/ActionProcedure';
import { ErrorSearchHeader } from '../../features/error-search/components/ErrorSearchHeader';
import { ManualPreview } from '../../features/error-search/components/ManualPreview';
import { RelatedManualList } from '../../features/error-search/components/RelatedManualList';

export function ErrorSearchResultPage() {
  return (
    <div className="mx-auto max-w-[1640px]">
      <ErrorSearchHeader />

      <div className="grid gap-6 lg:grid-cols-12">
        <ManualPreview />
        <ActionProcedure />
      </div>

      <div className="mt-7">
        <RelatedManualList />
      </div>
    </div>
  );
}
