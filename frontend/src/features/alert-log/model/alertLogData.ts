export type AlertSeverity = '긴급' | '경고' | '주의';
export type AlertStatus = '미확인' | '확인' | '완료';

export const alertFilters = ['전체', '긴급', '경고', '주의'] as const;

export const severityClassNames: Record<AlertSeverity, string> = {
  긴급: 'bg-red-600 text-white shadow-[0_0_22px_rgba(220,38,38,0.35)]',
  경고: 'bg-amber-500 text-white shadow-[0_0_22px_rgba(245,158,11,0.35)]',
  주의: 'bg-slate-500 text-white shadow-[0_0_18px_rgba(148,163,184,0.22)]',
};

export const statusClassNames: Record<AlertStatus, string> = {
  미확인: 'bg-red-600 text-white shadow-[0_0_22px_rgba(220,38,38,0.35)]',
  확인: 'bg-amber-500 text-white shadow-[0_0_22px_rgba(245,158,11,0.35)]',
  완료: 'bg-emerald-600 text-white shadow-[0_0_22px_rgba(5,150,105,0.35)]',
};
