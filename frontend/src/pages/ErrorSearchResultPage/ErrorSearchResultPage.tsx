import { useState } from 'react';
import { ClipboardCheck } from 'lucide-react';
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
import { ActionLogModal } from '../../features/error-search/components/result/ActionLogModal';
import { useErrorCodeSearch } from '../../features/error-search/hooks/useErrorCodeSearch';

export function ErrorSearchResultPage() {
  const [searchParams] = useSearchParams();
  const keyword = searchParams.get('q') || '';
  const { result, isLoading, errorMessage, refetch } = useErrorCodeSearch(keyword);
  const [isActionModalOpen, setIsActionModalOpen] = useState(false);

  if (isLoading) {
    return <ErrorSearchLoading />;
  }

  if (errorMessage) {
    return <ErrorSearchFailure message={errorMessage} onRetry={refetch} />;
  }

  const canRecordAction = !!(result && result.historyId !== null);

  return (
    <div className="mx-auto max-w-[1640px]">
      <ErrorSearchHeader />
      {result && <ErrorSearchAiSummary result={result} />}

      <div className="grid gap-6 lg:grid-cols-12">
        <ManualPreview result={result} />
        <ActionProcedure result={result} />
      </div>

      <div className="mt-7">
        <RelatedManualList />
      </div>

      {canRecordAction && (
        <div className="mt-8 flex justify-end">
          <button
            type="button"
            onClick={() => setIsActionModalOpen(true)}
            className="inline-flex h-12 items-center gap-2 rounded-xl bg-blue-600 px-6 text-[16px] font-black text-white shadow-[0_0_24px_rgba(37,99,235,0.35)] transition hover:bg-blue-500"
          >
            <ClipboardCheck className="h-5 w-5" />
            조치 결과 입력
          </button>
        </div>
      )}

      {result && result.historyId !== null && (
        <ActionLogModal
          historyId={result.historyId}
          query={result.keyword}
          open={isActionModalOpen}
          onClose={() => setIsActionModalOpen(false)}
        />
      )}
    </div>
  );
}
