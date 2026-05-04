import { Play } from 'lucide-react';

import { Panel } from '../../../shared/ui/Panel';
import { LogCodeViewer } from './LogCodeViewer';

export function VirtualLogInput() {
  return (
    <Panel className="p-5 lg:col-span-6 xl:col-span-6">
      <h2 className="text-[22px] font-black tracking-[-0.05em] text-white">가상 로그 입력</h2>

      <div className="mt-5">
        <LogCodeViewer />
      </div>

      <button
        type="button"
        className="mt-6 flex h-[56px] w-full items-center justify-center gap-3 rounded-xl border border-blue-500 bg-blue-600 text-[23px] font-black tracking-[-0.05em] text-white shadow-[0_0_26px_rgba(37,99,235,0.35)] transition hover:bg-blue-500"
      >
        <Play className="h-7 w-7 fill-white" />
        분석 시작
      </button>
    </Panel>
  );
}
