import { Download, FileText } from 'lucide-react';
import { useEffect, useState } from 'react';

import { Panel } from '../../../../shared/ui/Panel';
import { manualApi, type ManualSummary } from '../../infra/manual.api';

type ManualPreviewProps = {
  manual: ManualSummary | null;
};

export function ManualPreview({ manual }: ManualPreviewProps) {
  const [pdfUrl, setPdfUrl] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    let isActive = true;
    let objectUrl: string | null = null;

    setPdfUrl(null);
    setErrorMessage(null);

    if (!manual) {
      return () => {
        isActive = false;
      };
    }

    setIsLoading(true);

    manualApi
      .getManualPdf(manual.manual_id)
      .then((blob) => {
        objectUrl = URL.createObjectURL(blob);

        if (!isActive) {
          URL.revokeObjectURL(objectUrl);
          return;
        }

        setPdfUrl(objectUrl);
      })
      .catch((error: Error) => {
        if (isActive) {
          setErrorMessage(error.message || '매뉴얼 파일을 불러오지 못했습니다.');
        }
      })
      .finally(() => {
        if (isActive) {
          setIsLoading(false);
        }
      });

    return () => {
      isActive = false;
      if (objectUrl) {
        URL.revokeObjectURL(objectUrl);
      }
    };
  }, [manual]);

  return (
    <Panel className="min-h-[455px] p-6 lg:col-span-7">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="text-[24px] font-extrabold text-white">매뉴얼 미리보기</h2>
          {manual && (
            <p className="mt-1 text-[14px] font-medium text-slate-400">
              {manual.title} · {manual.category} · {manual.version}
            </p>
          )}
        </div>

        {pdfUrl && manual && (
          <a
            className="inline-flex h-10 items-center gap-2 rounded-lg border border-slate-700 bg-white/[0.03] px-3 text-[14px] font-bold text-slate-100 transition hover:border-blue-400/70 hover:text-blue-300"
            href={pdfUrl}
            download={`${manual.title}.pdf`}
          >
            <Download className="h-4 w-4" />
            다운로드
          </a>
        )}
      </div>

      <div className="mt-4 grid min-h-[520px] place-items-center overflow-hidden rounded-xl border border-slate-800 bg-slate-950/40">
        {!manual && (
          <div className="flex flex-col items-center gap-3 text-center text-slate-400">
            <FileText className="h-12 w-12 text-slate-500" />
            <p className="text-[15px] font-semibold">연결된 매뉴얼이 없습니다.</p>
          </div>
        )}

        {manual && isLoading && <p className="text-[15px] font-semibold text-slate-300">매뉴얼 파일을 불러오는 중입니다.</p>}

        {manual && errorMessage && !isLoading && <p className="px-6 text-center text-[15px] font-semibold text-red-300">{errorMessage}</p>}

        {manual && pdfUrl && !isLoading && !errorMessage && (
          <iframe className="h-[520px] w-full bg-white" src={pdfUrl} title={`${manual.title} preview`} />
        )}
      </div>
    </Panel>
  );
}
