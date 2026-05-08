import { AlertTriangle, RotateCcw } from 'lucide-react';
import { Link } from 'react-router-dom';

import { Panel } from '../../../../shared/ui/Panel';

type ErrorSearchFailureProps = {
  message: string;
  onRetry: () => void;
};

export function ErrorSearchFailure({ message, onRetry }: ErrorSearchFailureProps) {
  return (
    <div className="mx-auto flex min-h-[calc(100vh-220px)] max-w-[760px] items-center justify-center px-2 py-10">
      <Panel className="w-full p-8 text-center">
        <div className="mx-auto grid h-20 w-20 place-items-center rounded-full bg-red-500/10 text-red-300 shadow-[0_0_32px_rgba(239,68,68,0.22)]">
          <AlertTriangle className="h-10 w-10" />
        </div>

        <h1 className="mt-6 text-[32px] font-black tracking-[-0.06em] text-white">검색에 실패했습니다</h1>
        <p className="mx-auto mt-3 max-w-[520px] text-[17px] font-semibold leading-7 text-slate-400">{message}</p>

        <div className="mt-8 flex flex-wrap justify-center gap-3">
          <button
            type="button"
            onClick={onRetry}
            className="inline-flex h-12 items-center justify-center gap-2 rounded-xl bg-blue-600 px-6 text-[16px] font-black text-white shadow-[0_0_24px_rgba(37,99,235,0.32)] transition hover:bg-blue-500"
          >
            <RotateCcw className="h-5 w-5" />
            다시 검색
          </button>
          <Link
            to="/error-search"
            className="inline-flex h-12 items-center justify-center rounded-xl border border-slate-700 bg-slate-950/40 px-6 text-[16px] font-black text-slate-300 transition hover:border-blue-400/70 hover:text-blue-300"
          >
            검색 화면으로
          </Link>
        </div>
      </Panel>
    </div>
  );
}
