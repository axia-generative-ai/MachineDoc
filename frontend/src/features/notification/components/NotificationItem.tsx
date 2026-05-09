import { AlertTriangle, Search, X } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

import { useNotifications, type LiveNotification } from '../providers/NotificationsProvider';
import { notificationSeverityClassNames } from '../model/notificationData';

type NotificationItemProps = {
  notification: LiveNotification;
  onNavigate?: () => void;
};

export function NotificationItem({ notification, onNavigate }: NotificationItemProps) {
  const navigate = useNavigate();
  const { markAsRead, remove } = useNotifications();

  const canSearch = !!notification.suggestedErrorCode;

  const handleAnalyze = () => {
    if (!canSearch) return;
    markAsRead(notification.id);
    navigate(`/error-search/result?q=${encodeURIComponent(notification.suggestedErrorCode!)}`);
    onNavigate?.();
  };

  return (
    <article className="rounded-xl border border-slate-700/80 bg-slate-950/45 p-4 shadow-panel">
      <div className="mb-3 flex items-start justify-between gap-3">
        <button
          type="button"
          onClick={handleAnalyze}
          disabled={!canSearch}
          className={`flex min-w-0 flex-1 items-start gap-3 text-left ${canSearch ? 'cursor-pointer' : 'cursor-default'}`}
        >
          <span className={`grid h-10 w-10 shrink-0 place-items-center rounded-full border ${notificationSeverityClassNames[notification.level]}`}>
            <AlertTriangle className="h-6 w-6" />
          </span>
          <div className="min-w-0">
            <div className="mb-1 flex items-center gap-2">
              {notification.isUnread && <span className="rounded-full bg-red-500 px-2 py-0.5 text-[11px] font-black text-white">미확인</span>}
              <span className="text-[13px] font-black text-red-300">{notification.level} 알림</span>
            </div>
            <h3 className="truncate text-[17px] font-black tracking-[-0.04em] text-white">{notification.title}</h3>
            <p className="mt-1 text-[13px] font-semibold text-slate-400">
              {notification.equipment} · {notification.detail}
            </p>
            <p className="mt-1 text-[12px] font-medium text-slate-500">{notification.createdAt}</p>
          </div>
        </button>

        <button
          type="button"
          onClick={() => remove(notification.id)}
          className="grid h-8 w-8 shrink-0 place-items-center rounded-lg border border-slate-700 text-slate-400 transition hover:border-red-400/70 hover:text-red-300"
          aria-label="알림 닫기"
        >
          <X className="h-4 w-4" />
        </button>
      </div>

      <div className="grid grid-cols-2 gap-2">
        <button
          type="button"
          onClick={handleAnalyze}
          disabled={!canSearch}
          className="flex h-9 items-center justify-center gap-2 rounded-lg bg-blue-600 text-[13px] font-black text-white transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:bg-slate-700"
        >
          <Search className="h-4 w-4" />
          {canSearch ? `분석 (${notification.suggestedErrorCode})` : '분석 불가'}
        </button>
        <button
          type="button"
          onClick={() => markAsRead(notification.id)}
          className="h-9 rounded-lg border border-amber-400/60 bg-amber-400/5 text-[13px] font-black text-amber-300 transition hover:bg-amber-400/15"
        >
          확인
        </button>
      </div>
    </article>
  );
}
