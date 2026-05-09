import type { NotificationSeverity } from './notification.types';

export const notificationSeverityClassNames: Record<NotificationSeverity, string> = {
  긴급: 'text-red-400 bg-red-500/10 border-red-500/35',
  경고: 'text-amber-300 bg-amber-500/10 border-amber-500/35',
  주의: 'text-slate-200 bg-slate-500/10 border-slate-500/35',
};
