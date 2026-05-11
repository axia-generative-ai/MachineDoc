import { useEffect, useState } from 'react';
import { FileText, RefreshCw } from 'lucide-react';

import { Panel } from '../../../shared/ui/Panel';
import { manualApi, type ErrorCodeMapping } from '../../error-search/infra/manual.api';

type Props = {
  /** 부모에서 매뉴얼 업로드가 일어날 때 이 값을 증가시키면 자동 새로고침 */
  refreshKey?: number;
};

export function ErrorCodeMappingPanel({ refreshKey = 0 }: Props) {
  const [mappings, setMappings] = useState<ErrorCodeMapping[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const load = async () => {
    setIsLoading(true);
    setErrorMessage(null);
    try {
      const data = await manualApi.listErrorCodeMappings();
      setMappings(data);
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : '매핑 정보를 불러오지 못했습니다.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    void load();
  }, [refreshKey]);

  const totalManuals = new Set(mappings.map((m) => m.manualId)).size;

  return (
    <Panel className="overflow-hidden p-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-[24px] font-black tracking-[-0.05em] text-white">오류코드 ↔ 매뉴얼 매핑</h2>
          <p className="mt-1 text-[13px] font-semibold text-slate-400">
            {isLoading ? '불러오는 중...' : `매뉴얼 ${totalManuals}건 · 코드 ${mappings.length}건`}
          </p>
        </div>
        <button
          type="button"
          onClick={() => void load()}
          disabled={isLoading}
          className="grid h-10 w-10 place-items-center rounded-lg border border-slate-700 text-slate-300 transition hover:border-blue-400/60 hover:text-blue-300 disabled:opacity-50"
          aria-label="새로고침"
        >
          <RefreshCw className={`h-5 w-5 ${isLoading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {errorMessage && (
        <p className="mt-4 rounded-lg border border-red-500/40 bg-red-500/10 px-4 py-3 text-[14px] font-bold text-red-300">
          {errorMessage}
        </p>
      )}

      <div className="mt-6 max-h-[460px] overflow-y-auto rounded-xl border border-slate-700/80">
        {!isLoading && mappings.length === 0 ? (
          <p className="px-6 py-10 text-center text-[14px] font-bold text-slate-500">
            등록된 매핑이 없습니다. 좌측에서 매뉴얼을 업로드하면 자동으로 추가됩니다.
          </p>
        ) : (
          mappings.map((item) => (
            <article
              key={item.errorCodeId}
              className="grid grid-cols-[110px_1fr_auto] items-center gap-4 border-b border-slate-700/80 px-6 py-3 last:border-b-0 hover:bg-white/[0.03]"
            >
              <span className="font-mono text-[18px] font-black text-blue-300">{item.codeName}</span>
              <div className="min-w-0">
                <p className="truncate text-[16px] font-bold text-white">{item.manualTitle}</p>
                <p className="text-[12px] font-semibold text-slate-500">
                  manual_id={item.manualId} · {item.category} · {item.version}
                </p>
              </div>
              <FileText className="h-5 w-5 text-slate-400" />
            </article>
          ))
        )}
      </div>
    </Panel>
  );
}
