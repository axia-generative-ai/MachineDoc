import { useEffect, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Play } from 'lucide-react';

import { Panel } from '../../../shared/ui/Panel';
import { detectionApi, type EquipmentLogResult } from '../infra/detection.api';

type Props = {
  onResult: (result: EquipmentLogResult) => void;
};

export function VirtualLogInput({ onResult }: Props) {
  const equipmentsQuery = useQuery({
    queryKey: ['equipment', 'list'],
    queryFn: detectionApi.listEquipments,
    staleTime: 60_000,
  });

  const equipments = equipmentsQuery.data ?? [];
  const [equipmentCode, setEquipmentCode] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [lastResult, setLastResult] = useState<EquipmentLogResult | null>(null);

  // 목록 로드 후 첫 번째 설비를 디폴트로 선택. 사용자가 이미 선택했으면 유지.
  useEffect(() => {
    if (!equipmentCode && equipments.length > 0) {
      setEquipmentCode(equipments[0].equipmentCode);
    }
  }, [equipments, equipmentCode]);

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
          disabled={equipmentsQuery.isLoading || equipments.length === 0}
          className="h-12 w-full rounded-lg border border-slate-700/90 bg-slate-950/45 px-4 text-[16px] font-semibold text-white outline-none transition focus:border-blue-400/70 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {equipmentsQuery.isLoading && (
            <option value="" className="bg-slate-950 text-white">설비 목록 불러오는 중...</option>
          )}
          {!equipmentsQuery.isLoading && equipments.length === 0 && (
            <option value="" className="bg-slate-950 text-white">등록된 설비가 없습니다</option>
          )}
          {equipments.map((eq) => (
            <option key={eq.equipmentId} value={eq.equipmentCode} className="bg-slate-950 text-white">
              {eq.equipmentCode} ({eq.location})
            </option>
          ))}
        </select>
        {equipmentsQuery.isError && (
          <span className="mt-2 block text-[13px] font-semibold text-red-300">
            설비 목록을 가져오지 못했습니다.
          </span>
        )}
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
        disabled={isLoading || !equipmentCode}
        className="mt-6 flex h-[56px] w-full items-center justify-center gap-3 rounded-xl border border-blue-500 bg-blue-600 text-[23px] font-black tracking-[-0.05em] text-white shadow-[0_0_26px_rgba(37,99,235,0.35)] transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:bg-slate-700 disabled:text-slate-400 disabled:shadow-none"
      >
        <Play className="h-7 w-7 fill-white" />
        {isLoading ? '분석 중...' : '분석 시작'}
      </button>
    </Panel>
  );
}
