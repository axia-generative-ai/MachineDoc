import { ChevronLeft, ChevronRight } from 'lucide-react';

import { Panel } from '../../../shared/ui/Panel';

const skeletonLines = [
  'w-36',
  'w-72',
  'w-[420px]',
  'w-[560px]',
  'w-[560px]',
  'w-[560px]',
  'w-[420px]',
  'w-[520px]',
  'w-[360px]',
  'w-[300px]',
  'w-[570px]',
];

export function ManualPreview() {
  return (
    <Panel className="min-h-[455px] p-6 lg:col-span-7">
      <h2 className="text-[24px] font-extrabold tracking-[-0.04em] text-white">매뉴얼 미리보기</h2>

      <div className="mt-4 rounded-xl bg-slate-950/20 p-2">
        <p className="mb-4 text-center text-[19px] font-bold text-white">Valve Manual p.32</p>
        <div className="space-y-4">
          <div className={`h-2 rounded-full bg-slate-600/70 ${skeletonLines[0]}`} />
          <div className={`h-2 rounded-full bg-slate-600/70 ${skeletonLines[1]}`} />

          <div className="flex gap-6 py-2">
            <div className="h-24 w-44 rounded bg-blue-500/10" />
            <div className="flex flex-1 flex-col justify-center gap-3">
              {skeletonLines.slice(2, 6).map((line) => (
                <div key={line} className={`h-2 rounded-full bg-slate-600/70 ${line}`} />
              ))}
            </div>
          </div>

          {skeletonLines.slice(6).map((line, index) => (
            <div key={`${line}-${index}`} className="flex items-center gap-4">
              {index > 1 && <span className="h-1.5 w-1.5 rounded-full bg-slate-600/80" />}
              <div className={`h-2 rounded-full bg-slate-600/70 ${line}`} />
            </div>
          ))}
        </div>
      </div>

      <div className="mt-7 flex items-center justify-between text-[14px] font-medium text-slate-500">
        <span>출처: Valve_Manual.pdf p.32</span>
        <div className="flex items-center gap-5 text-[17px] text-slate-300">
          <button className="grid h-10 w-10 place-items-center rounded-lg border border-slate-700 bg-white/[0.02] transition hover:border-blue-400/60 hover:text-blue-300">
            <ChevronLeft className="h-5 w-5" />
          </button>
          <span>32 / 128</span>
          <button className="grid h-10 w-10 place-items-center rounded-lg border border-slate-700 bg-white/[0.02] transition hover:border-blue-400/60 hover:text-blue-300">
            <ChevronRight className="h-5 w-5" />
          </button>
        </div>
      </div>
    </Panel>
  );
}
