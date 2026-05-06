import { ChevronDown } from 'lucide-react';

import { manualSettings } from '../model/adminData';
import { Panel } from '../../../shared/ui/Panel';

export function ManualSettingsPanel() {
  return (
    <Panel className="p-6 lg:col-span-5">
      <h2 className="text-[24px] font-black tracking-[-0.05em] text-white">설정값</h2>

      <div className="mt-6 space-y-5">
        <label className="block">
          <span className="mb-2 block text-[16px] font-semibold text-slate-400">매뉴얼명</span>
          <input className="h-12 w-full rounded-lg border border-slate-700 bg-slate-950/30 px-4 text-[18px] font-semibold text-white outline-none" value={manualSettings.manualName} readOnly />
        </label>

        <label className="block">
          <span className="mb-2 block text-[16px] font-semibold text-slate-400">카테고리</span>
          <div className="flex h-12 items-center justify-between rounded-lg border border-slate-700 bg-slate-950/30 px-4 text-[18px] font-semibold text-white">
            {manualSettings.category}
            <ChevronDown className="h-5 w-5 text-slate-400" />
          </div>
        </label>

        <label className="block">
          <span className="mb-2 block text-[16px] font-semibold text-slate-400">버전</span>
          <input className="h-12 w-full rounded-lg border border-slate-700 bg-slate-950/30 px-4 text-[18px] font-semibold text-white outline-none" value={manualSettings.version} readOnly />
        </label>

        <label className="block">
          <span className="mb-2 block text-[16px] font-semibold text-slate-400">오류코드</span>
          <input className="h-12 w-full rounded-lg border border-slate-700 bg-slate-950/30 px-4 text-[18px] font-semibold text-white outline-none" value={manualSettings.errorCode} readOnly />
        </label>
      </div>
    </Panel>
  );
}
