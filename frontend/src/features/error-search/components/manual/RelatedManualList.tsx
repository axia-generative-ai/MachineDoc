import { useEffect, useState } from 'react';

import { manualApi, type RelatedManual } from '../../infra/manual.api';
import { RelatedManualCard } from './RelatedManualCard';

type Props = {
  category?: string;
  equipmentCode?: string;
};

export function RelatedManualList({ category, equipmentCode }: Props) {
  const [manuals, setManuals] = useState<RelatedManual[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setIsLoading(true);
    setErrorMessage(null);
    manualApi
      .search({ category, equipmentCode })
      .then((data) => {
        if (!cancelled) setManuals(data);
      })
      .catch((error) => {
        if (!cancelled) setErrorMessage(error?.message ?? '매뉴얼 목록을 불러오지 못했습니다.');
      })
      .finally(() => {
        if (!cancelled) setIsLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [category, equipmentCode]);

  if (isLoading) {
    return <p className="text-[14px] font-bold text-slate-400">매뉴얼을 불러오는 중...</p>;
  }

  if (errorMessage) {
    return (
      <p className="rounded-lg border border-red-500/40 bg-red-500/10 px-4 py-3 text-[14px] font-bold text-red-300">
        {errorMessage}
      </p>
    );
  }

  if (manuals.length === 0) {
    return <p className="text-[14px] font-bold text-slate-400">관련 매뉴얼이 없습니다.</p>;
  }

  return (
    <div className="grid gap-5 lg:grid-cols-3">
      {manuals.map((manual) => (
        <RelatedManualCard key={manual.manualId} manual={manual} />
      ))}
    </div>
  );
}
