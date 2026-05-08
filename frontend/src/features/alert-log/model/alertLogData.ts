export type AlertSeverity = '긴급' | '경고' | '주의';
export type AlertStatus = '미확인' | '확인' | '해결';

export const alertFilters = ['전체', '긴급', '경고', '주의'] as const;

export const alertLogRows = [
  {
    time: '14:32',
    severity: '긴급',
    equipment: 'M-102',
    message: '라인A 모터 진동 초과',
    status: '미확인',
  },
  {
    time: '13:45',
    severity: '경고',
    equipment: 'E-204',
    message: '밸브 온도 상승',
    status: '확인',
  },
  {
    time: '11:20',
    severity: '주의',
    equipment: 'S-101',
    message: '센서 통신 지연',
    status: '해결',
  },
  {
    time: '09:15',
    severity: '경고',
    equipment: 'M-102',
    message: '모터 일시 정지',
    status: '해결',
  },
  {
    time: '08:02',
    severity: '주의',
    equipment: 'V-318',
    message: '밸브 압력 변화',
    status: '해결',
  },
] as const;

export const severityClassNames: Record<AlertSeverity, string> = {
  긴급: 'bg-red-600 text-white shadow-[0_0_22px_rgba(220,38,38,0.35)]',
  경고: 'bg-amber-500 text-white shadow-[0_0_22px_rgba(245,158,11,0.35)]',
  주의: 'bg-slate-500 text-white shadow-[0_0_18px_rgba(148,163,184,0.22)]',
};

export const statusClassNames: Record<AlertStatus, string> = {
  미확인: 'bg-red-600 text-white shadow-[0_0_22px_rgba(220,38,38,0.35)]',
  확인: 'bg-amber-500 text-white shadow-[0_0_22px_rgba(245,158,11,0.35)]',
  해결: 'bg-emerald-600 text-white shadow-[0_0_22px_rgba(5,150,105,0.35)]',
};
