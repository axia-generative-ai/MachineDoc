import { Loader2, Search, ShieldCheck, X } from 'lucide-react';
import { useNavigate, useSearchParams } from 'react-router-dom';

import { Panel } from '../../../../shared/ui/Panel';

type SearchLoadingStep = {
  label: string;
  state: 'done' | 'active' | 'pending';
};

const text = {
  verifyingCode: '\uC624\uB958\uCF54\uB4DC \uAC80\uC99D',
  searchingManual: '\uB9E4\uB274\uC5BC \uAC80\uC0C9',
  creatingProcedure: 'AI \uC870\uCE58 \uC808\uCC28 \uC0DD\uC131',
  searching: '\uAC80\uC0C9 \uC911...',
  prefix: '\uC624\uB958\uCF54\uB4DC',
  suffix: '\uC5D0 \uB300\uD55C \uB9E4\uB274\uC5BC\uACFC \uC870\uCE58 \uC808\uCC28\uB97C \uCC3E\uACE0 \uC788\uC2B5\uB2C8\uB2E4',
  cancel: '\uAC80\uC0C9 \uC911\uB2E8',
} as const;

const loadingSteps: SearchLoadingStep[] = [
  { label: text.verifyingCode, state: 'done' },
  { label: text.searchingManual, state: 'active' },
  { label: text.creatingProcedure, state: 'pending' },
];

export function ErrorSearchLoading() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const keyword = searchParams.get('q') || 'E-204';

  return (
    <div className="mx-auto flex min-h-[calc(100vh-210px)] max-w-[960px] items-center justify-center px-2 py-10">
      <Panel className="relative w-full overflow-hidden p-8 text-center md:p-10">
        <div className="absolute inset-x-10 top-0 h-px bg-gradient-to-r from-transparent via-blue-400/70 to-transparent" />
        <div className="absolute left-1/2 top-10 h-48 w-48 -translate-x-1/2 rounded-full bg-blue-500/10 blur-3xl" />

        <div className="relative mx-auto grid h-24 w-24 place-items-center rounded-full border border-blue-400/40 bg-blue-500/10 shadow-[0_0_42px_rgba(37,99,235,0.38)]">
          <Loader2 className="h-12 w-12 animate-spin text-blue-400" />
        </div>

        <div className="relative mt-7">
          <p className="text-[16px] font-black tracking-[0.24em] text-blue-300">AI MANUAL SEARCH</p>
          <h1 className="mt-3 text-[34px] font-black tracking-[-0.06em] text-white md:text-[42px]">{text.searching}</h1>
          <p className="mt-3 text-[17px] font-semibold tracking-[-0.04em] text-slate-400 md:text-[19px]">
            {text.prefix} <span className="font-black text-blue-300">{keyword}</span>{text.suffix}
          </p>
        </div>

        <div className="relative mx-auto mt-9 max-w-[620px]">
          <div className="absolute left-[12%] right-[12%] top-5 h-px bg-slate-700" />
          <div className="relative grid grid-cols-3 gap-3">
            {loadingSteps.map((step) => (
              <div key={step.label} className="flex flex-col items-center gap-3">
                <span
                  className={`grid h-10 w-10 place-items-center rounded-full border text-sm font-black transition ${
                    step.state === 'done'
                      ? 'border-blue-400 bg-blue-600 text-white shadow-[0_0_22px_rgba(37,99,235,0.48)]'
                      : step.state === 'active'
                        ? 'border-blue-300 bg-slate-950 text-blue-300 shadow-[0_0_22px_rgba(59,130,246,0.32)]'
                        : 'border-slate-600 bg-slate-950 text-slate-500'
                  }`}
                >
                  {step.state === 'done' ? <ShieldCheck className="h-5 w-5" /> : step.state === 'active' ? <Search className="h-5 w-5" /> : '3'}
                </span>
                <span className={`text-[14px] font-bold ${step.state === 'pending' ? 'text-slate-500' : 'text-slate-200'}`}>{step.label}</span>
              </div>
            ))}
          </div>
        </div>

        <button
          type="button"
          onClick={() => navigate('/error-search')}
          className="relative mt-9 inline-flex h-12 min-w-[210px] items-center justify-center gap-2 rounded-xl border border-red-400/70 bg-red-500/10 px-7 text-[16px] font-black text-red-300 transition hover:bg-red-500/20 hover:text-red-200"
        >
          <X className="h-5 w-5" />
          {text.cancel}
        </button>
      </Panel>
    </div>
  );
}



