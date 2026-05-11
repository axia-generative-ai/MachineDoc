import { useState } from 'react';
import { Play } from 'lucide-react';

import { Panel } from '../../../shared/ui/Panel';
import { detectionApi, equipmentList, type EquipmentLogResult } from '../infra/detection.api';

type Props = {
  onResult: (result: EquipmentLogResult) => void;
};

export function VirtualLogInput({ onResult }: Props) {
  const [equipmentCode, setEquipmentCode] = useState<string>(equipmentList[0].code);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [lastResult, setLastResult] = useState<EquipmentLogResult | null>(null);

  const handleSubmit = async () => {
    setIsLoading(true);
    setErrorMessage(null);
    try {
      const result = await detectionApi.createVirtualLog(equipmentCode);
      setLastResult(result);
      onResult(result);
    } catch (error) {
      const message = error instanceof Error ? error.message : '가상 로그 생성에 실패했습니다.';
      setErrorMessage(message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Panel className="p-5 lg:col-span-6 xl:col-span-6">
      <h2 className="text-[22px] font-black tracking-[-0.05em] text-white">가상 로그 입력</h2>

      <label className="mt-5 block">
        <span className="mb-2 block text-[14px] font-bold text-slate-400">대상 설비</span>
        <select
          value={equipmentCode}
          onChange={(event) => setEquipmentCode(event.target.value)}
          className="h-12 w-full rounded-lg border border-slate-700/90 bg-slate-950/45 px-4 text-[16px] font-semibold text-white outline-none transition focus:border-blue-400/70"
        >
          {equipmentList.map((item) => (
            <option key={item.code} value={item.code} className="bg-slate-950 text-white">
              {item.label} ({item.code})
            </option>
          ))}
        </select>
      </label>

      <div className="mt-5 overflow-hidden rounded-xl border border-slate-700/80 bg-slate-950/20 p-4 font-mono text-[14px] leading-[1.85] text-slate-300">
        {lastResult ? (
          <pre className="m-0 whitespace-pre-wrap">
{JSON.stringify(
  {
    log_id: lastResult.logId,
    equipment_id: lastResult.equipmentId,
    data_type: lastResult.dataType,
    value: lastResult.value,
    status: lastResult.status,
    occurred_at: lastResult.occurredAt,
  },
  null,
  2,
)}
          </pre>
        ) : (
          <p className="text-slate-500">설비를 선택한 후 "분석 시작"을 눌러 가상 센서 로그를 생성하세요.</p>
        )}
      </div>

      {errorMessage && (
        <p className="mt-4 rounded-lg border border-red-500/40 bg-red-500/10 px-4 py-3 text-[14px] font-bold text-red-300">
          {errorMessage}
        </p>
      )}

      <button
        type="button"
        onClick={handleSubmit}
        disabled={isLoading}
        className="mt-6 flex h-[56px] w-full items-center justify-center gap-3 rounded-xl border border-blue-500 bg-blue-600 text-[23px] font-black tracking-[-0.05em] text-white shadow-[0_0_26px_rgba(37,99,235,0.35)] transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:bg-slate-700 disabled:text-slate-400 disabled:shadow-none"
      >
        <Play className="h-7 w-7 fill-white" />
        {isLoading ? '분석 중...' : '분석 시작'}
      </button>
    </Panel>
  );
}
