export type NotificationSeverity = '긴급' | '경고' | '주의';

export const notifications = [
  {
    id: 'alert-1',
    severity: '긴급',
    title: 'LINE_A 모터 진동 임계 초과',
    equipment: 'EQ-MOTOR-001',
    detail: '진동 1180Hz (error_threshold 1100 초과)',
    createdAt: '2026-05-06 14:32',
    isUnread: true,
  },
  {
    id: 'alert-2',
    severity: '경고',
    title: 'LINE_B 프레스 온도 상승',
    equipment: 'EQ-PRESS-003',
    detail: '온도 89.9°C (warning 70 / error 90)',
    createdAt: '2026-05-06 13:45',
    isUnread: true,
  },
  {
    id: 'alert-3',
    severity: '주의',
    title: 'LINE_A 컨베이어 진동 변동',
    equipment: 'EQ-CONVEYOR-002',
    detail: '진동 820Hz (warning 800 근접)',
    createdAt: '2026-05-06 11:20',
    isUnread: true,
  },
] as const;

export const notificationSeverityClassNames: Record<NotificationSeverity, string> = {
  긴급: 'text-red-400 bg-red-500/10 border-red-500/35',
  경고: 'text-amber-300 bg-amber-500/10 border-amber-500/35',
  주의: 'text-slate-200 bg-slate-500/10 border-slate-500/35',
};
