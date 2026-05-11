import { AlertTriangle, Search, ShieldCheck, Wrench } from 'lucide-react';

import { Panel } from '../../../shared/ui/Panel';
import type { EquipmentLogResult } from '../infra/detection.api';
import { detectionColorClasses, type DetectionColor } from '../model/detectionTheme';

type Props = {
  result: EquipmentLogResult | null;
};

type ResultRow = {
  label: string;
  value: string;
  icon: typeof AlertTriangle;
  color: DetectionColor;
};

function buildRows(result: EquipmentLogResult): ResultRow[] {
  const isAnomaly = result.status !== '정상';
  const unit = result.dataType === 'TEMPERATURE' ? '°C' : 'Hz';
  const causeMap: Record<string, string> = {
    TEMPERATURE: '온도 임계값 초과',
    VIBRATION: '진동 임계값 초과',
  };
  const actionMap: Record<string, string> = {
    TEMPERATURE: '냉각 시스템 점검, 부하 감소',
    VIBRATION: '베어링 점검, 윤활 확인',
  };
  const colorByStatus: Record<string, DetectionColor> = {
    정상: 'green',
    위험: 'amber',
    오류: 'red',
  };

  return [
    {
      label: '이상 여부',
      value: isAnomaly ? `이상 (${result.status})` : '정상',
      icon: AlertTriangle,
      color: isAnomaly ? 'red' : 'green',
    },
    {
      label: '측정값',
      value: `${result.value.toFixed(2)} ${unit} (${result.dataType})`,
      icon: Search,
      color: 'blue',
    },
    {
      label: '추정 원인',
      value: isAnomaly ? causeMap[result.dataType] ?? '센서 데이터 이상' : '특이 사항 없음',
      icon: Search,
      color: 'blue',
    },
    {
      label: '권장 조치',
      value: isAnomaly ? actionMap[result.dataType] ?? '매뉴얼 확인 후 점검' : '정기 점검 유지',
      icon: Wrench,
      color: 'amber',
    },
    {
      label: '상태',
      value: result.status,
      icon: ShieldCheck,
      color: colorByStatus[result.status] ?? 'blue',
    },
  ];
}

export function AnalysisResultPanel({ result }: Props) {
  return (
    <Panel className="p-5 lg:col-span-6 xl:col-span-6">
      <h2 className="text-[22px] font-black tracking-[-0.05em] text-white">분석 결과</h2>

      <div className="mt-5 space-y-4">
        {result === null ? (
          <p className="rounded-xl border border-slate-700/80 bg-slate-900/20 px-5 py-6 text-center text-[15px] font-semibold text-slate-500">
            가상 로그 분석을 실행하면 결과가 여기에 표시됩니다.
          </p>
        ) : (
          buildRows(result).map((row) => {
            const Icon = row.icon;
            const palette = detectionColorClasses[row.color];
            return (
              <article
                key={row.label}
                className="grid min-h-[88px] grid-cols-[56px_1fr_auto] items-center gap-4 rounded-xl border border-slate-700/80 bg-slate-900/20 px-5 py-4 shadow-panel"
              >
                <div className={`grid h-12 w-12 place-items-center rounded-full ${palette.bg}`}>
                  <Icon className={`h-7 w-7 ${palette.icon}`} strokeWidth={2.2} />
                </div>
                <h3 className="text-[20px] font-black tracking-[-0.05em] text-white">{row.label}</h3>
                <p className={`text-right text-[18px] font-black tracking-[-0.05em] ${palette.text}`}>{row.value}</p>
              </article>
            );
          })
        )}
      </div>

      <p className="mt-6 text-center text-[16px] font-semibold tracking-[-0.04em] text-slate-500">
        룰 1차 분석 (가상 로그 생성 + 임계값 판정). 상세 조치는 오류코드 검색 페이지에서 확인하세요.
      </p>
    </Panel>
  );
}
