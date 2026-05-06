import { AlertTriangle, X } from 'lucide-react';

import type { notifications } from '../model/notificationData';
import { notificationSeverityClassNames } from '../model/notificationData';

type NotificationItemProps = {
  notification: (typeof notifications)[number];
};

export function NotificationItem({ notification }: NotificationItemProps) {
  return (
    <article className="rounded-xl border border-slate-700/80 bg-slate-950/45 p-4 shadow-panel">
      <div className="mb-3 flex items-start justify-between gap-3">
        <div className="flex min-w-0 items-start gap-3">
          <span className={`grid h-10 w-10 shrink-0 place-items-center rounded-full border ${notificationSeverityClassNames[notification.severity]}`}>
            <AlertTriangle className="h-6 w-6" />
          </span>
          <div className="min-w-0">
            <div className="mb-1 flex items-center gap-2">
              {notification.isUnread && <span className="rounded-full bg-red-500 px-2 py-0.5 text-[11px] font-black text-white">미확인</span>}
              <span className="text-[13px] font-black text-red-300">{notification.severity} 알림</span>
            </div>
            <h3 className="truncate text-[17px] font-black tracking-[-0.04em] text-white">{notification.title}</h3>
            <p className="mt-1 text-[13px] font-semibold text-slate-400">
              {notification.equipment} · {notification.detail}
            </p>
            <p className="mt-1 text-[12px] font-medium text-slate-500">{notification.createdAt}</p>
          </div>
        </div>

        <button type="button" className="grid h-8 w-8 shrink-0 place-items-center rounded-lg border border-slate-700 text-slate-400 transition hover:border-red-400/70 hover:text-red-300" aria-label="알림 닫기">
          <X className="h-4 w-4" />
        </button>
      </div>

      <div className="grid grid-cols-2 gap-2">
        <button type="button" className="h-9 rounded-lg bg-red-500 text-[13px] font-black text-white transition hover:bg-red-400">
          분석하기
        </button>
        <button type="button" className="h-9 rounded-lg border border-amber-400/60 bg-amber-400/5 text-[13px] font-black text-amber-300 transition hover:bg-amber-400/15">
          저장
        </button>
      </div>
    </article>
  );
}
