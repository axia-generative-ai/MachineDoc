import { useSearchParams } from 'react-router-dom';

import {
  ActionProcedure,
  ErrorSearchAiSummary,
  ErrorSearchFailure,
  ErrorSearchHeader,
  ErrorSearchLoading,
  ManualPreview,
  RelatedManualList,
} from '../../features/error-search/components';
import { useErrorCodeSearch } from '../../features/error-search/hooks/useErrorCodeSearch';

export function ErrorSearchResultPage() {
  const [searchParams] = useSearchParams();
  const keyword = searchParams.get('q') || '';
  const { result, isLoading, errorMessage, refetch } = useErrorCodeSearch(keyword);

  if (isLoading) {
    return <ErrorSearchLoading />;
  }

  if (errorMessage) {
    return <ErrorSearchFailure message={errorMessage} onRetry={refetch} />;
  }

  return (
    <div className="mx-auto max-w-[1640px]">
      <ErrorSearchHeader />
      {result && <ErrorSearchAiSummary result={result} />}

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
