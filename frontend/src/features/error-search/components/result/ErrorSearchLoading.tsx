import { FileSearch, Loader2, Search, ShieldCheck, Sparkles, X } from 'lucide-react';
import { useEffect, useMemo, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';

import { Panel } from '../../../../shared/ui/Panel';

type SearchLoadingStep = {
  label: string;
  description: string;
  icon: typeof ShieldCheck;
};

const text = {
  searching: '검색 중...',
  prefix: '오류코드',
  suffix: '에 대한 매뉴얼과 조치 절차를 찾고 있습니다',
  cancel: '검색 중단',
} as const;

const loadingSteps: SearchLoadingStep[] = [
  {
    label: '오류코드 검증',
    description: '등록된 코드와 연결 매뉴얼을 확인합니다.',
    icon: ShieldCheck,
  },
  {
    label: '매뉴얼 검색',
    description: '관련 문서와 오류 코드 섹션을 찾습니다.',
    icon: FileSearch,
  },
  {
    label: 'AI 조치 절차 생성',
    description: '분석 결과와 권장 조치를 정리합니다.',
    icon: Sparkles,
  },
];

const stepDurations = [900, 1700, 2600];

function getStepState(index: number, currentStep: number) {
  if (index < currentStep) return 'done';
  if (index === currentStep) return 'active';
  return 'pending';
}

export function ErrorSearchLoading() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const keyword = searchParams.get('q') || 'E-204';
  const [currentStep, setCurrentStep] = useState(0);
  const activeStep = loadingSteps[currentStep] ?? loadingSteps[loadingSteps.length - 1];
  const progress = useMemo(() => ((currentStep + 1) / loadingSteps.length) * 100, [currentStep]);

  useEffect(() => {
    const timers = stepDurations.map((duration, index) =>
      window.setTimeout(() => {
        setCurrentStep(Math.min(index + 1, loadingSteps.length - 1));
      }, duration),
    );

    return () => {
      timers.forEach((timer) => window.clearTimeout(timer));
    };
  }, []);

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
          <h1 className="mt-3 text-[34px] font-black text-white md:text-[42px]">{text.searching}</h1>
          <p className="mt-3 text-[17px] font-semibold text-slate-400 md:text-[19px]">
            {text.prefix} <span className="font-black text-blue-300">{keyword}</span>{text.suffix}
          </p>
          <p className="mt-4 inline-flex rounded-lg border border-blue-400/20 bg-blue-500/10 px-4 py-2 text-[15px] font-bold text-blue-100">
            {activeStep.description}
          </p>
        </div>

        <div className="relative mx-auto mt-9 max-w-[680px]">
          <div className="absolute left-[12%] right-[12%] top-5 h-px bg-slate-700" />
          <div className="absolute left-[12%] top-5 h-px bg-blue-500 transition-all duration-700" style={{ width: `${Math.max(progress - 25, 0)}%` }} />

          <div className="relative grid grid-cols-3 gap-3">
            {loadingSteps.map((step, index) => {
              const StepIcon = step.icon;
              const state = getStepState(index, currentStep);

              return (
                <div key={step.label} className="flex flex-col items-center gap-3">
                  <span
                    className={`grid h-10 w-10 place-items-center rounded-full border text-sm font-black transition duration-500 ${
                      state === 'done'
                        ? 'border-blue-400 bg-blue-600 text-white shadow-[0_0_22px_rgba(37,99,235,0.48)]'
                        : state === 'active'
                          ? 'border-blue-300 bg-slate-950 text-blue-300 shadow-[0_0_22px_rgba(59,130,246,0.32)]'
                          : 'border-slate-600 bg-slate-950 text-slate-500'
                    }`}
                  >
                    {state === 'done' ? <ShieldCheck className="h-5 w-5" /> : state === 'active' ? <StepIcon className="h-5 w-5" /> : index + 1}
                  </span>

                  <div className="min-h-[56px]">
                    <span className={`block text-[14px] font-bold ${state === 'pending' ? 'text-slate-500' : 'text-slate-100'}`}>{step.label}</span>
                    {state === 'active' && (
                      <span className="mt-1 flex items-center justify-center gap-1.5 text-[12px] font-semibold text-blue-300">
                        <Search className="h-3.5 w-3.5" />
                        진행 중
                      </span>
                    )}
                    {state === 'done' && <span className="mt-1 block text-[12px] font-semibold text-emerald-300">완료</span>}
                  </div>
                </div>
              );
            })}
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
