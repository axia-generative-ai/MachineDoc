import { useEffect, useState } from 'react';
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
import { manualApi, type ManualSummary } from '../../features/error-search/infra/manual.api';

export function ErrorSearchResultPage() {
  const [searchParams] = useSearchParams();
  const keyword = searchParams.get('q') || '';
  const { result, isLoading, errorMessage, refetch } = useErrorCodeSearch(keyword);
  const [manuals, setManuals] = useState<ManualSummary[]>([]);
  const [selectedManual, setSelectedManual] = useState<ManualSummary | null>(null);
  const [manualsLoading, setManualsLoading] = useState(false);
  const [manualsErrorMessage, setManualsErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    let isActive = true;

    setManualsLoading(true);
    setManualsErrorMessage(null);

    manualApi
      .searchManuals()
      .then((nextManuals) => {
        if (!isActive) return;

        setManuals(nextManuals);
        setSelectedManual(nextManuals[0] ?? null);
      })
      .catch((error: Error) => {
        if (isActive) {
          setManualsErrorMessage(error.message || '관련 매뉴얼을 불러오지 못했습니다.');
        }
      })
      .finally(() => {
        if (isActive) {
          setManualsLoading(false);
        }
      });

    return () => {
      isActive = false;
    };
  }, []);

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
        <ManualPreview manual={selectedManual} />
        <ActionProcedure />
      </div>

      <div className="mt-7">
        <RelatedManualList
          manuals={manuals}
          selectedManualId={selectedManual?.manual_id}
          isLoading={manualsLoading}
          errorMessage={manualsErrorMessage}
          onSelect={setSelectedManual}
        />
      </div>
    </div>
  );
}
