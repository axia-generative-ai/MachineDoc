export type NotificationSeverity = '긴급' | '경고' | '주의';

export const notifications = [
  {
    id: 'alert-1',
    severity: '긴급',
    title: '라인A 모터 이상 감지',
    equipment: 'M-102',
    detail: '진동값 7.2 (정상 초과)',
    createdAt: '2026-05-06 14:32',
    isUnread: true,
  },
  {
    id: 'alert-2',
    severity: '경고',
    title: '라인B Valve 이상 감지',
    equipment: 'E-204',
    detail: '온도 이상 89.9 (정상 초과)',
    createdAt: '2026-05-06 13:45',
    isUnread: true,
  },
  {
    id: 'alert-3',
    severity: '주의',
    title: '센서 통신 지연',
    equipment: 'S-101',
    detail: '응답 지연 2.4초',
    createdAt: '2026-05-06 11:20',
    isUnread: true,
  },
] as const;

export const notificationSeverityClassNames: Record<NotificationSeverity, string> = {
  긴급: 'text-red-400 bg-red-500/10 border-red-500/35',
  경고: 'text-amber-300 bg-amber-500/10 border-amber-500/35',
  주의: 'text-slate-200 bg-slate-500/10 border-slate-500/35',
};
