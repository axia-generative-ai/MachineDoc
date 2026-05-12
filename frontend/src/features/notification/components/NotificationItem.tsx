import { AlertTriangle, Search, X } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

import { notificationSeverityClassNames } from '../model/notificationData';
import type { RealtimeNotification } from '../model/notification.types';

type NotificationItemProps = {
  notification: RealtimeNotification;
  onDismiss: (id: string) => void;
  onNavigate?: () => void;
};

export function NotificationItem({ notification, onDismiss, onNavigate }: NotificationItemProps) {
  const navigate = useNavigate();
  // 알림 1건당 코드 1개 (anomaly_rules.json 풀에서 BE가 random.choice).
  // suggestedErrorCodes는 하위호환용 배열 (길이 0 또는 1).
  const code = notification.suggestedErrorCode
    ?? notification.suggestedErrorCodes?.[0]
    ?? null;
  const canSearch = Boolean(code);

  const handleAnalyze = () => {
    if (!code) return;
    navigate(`/error-search/result?q=${encodeURIComponent(code)}`);
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
          <span className={`grid h-10 w-10 shrink-0 place-items-center rounded-full border ${notificationSeverityClassNames[notification.severity]}`}>
            <AlertTriangle className="h-6 w-6" />
          </span>
          <div className="min-w-0">
            <div className="mb-1 flex items-center gap-2">
              {notification.isUnread && <span className="rounded-full bg-red-500 px-2 py-0.5 text-[11px] font-black text-white">미확인</span>}
              <span className="text-[13px] font-black text-red-300">{notification.severity} 알림</span>
            </div>
            <h3 className="truncate text-[17px] font-black text-white">{notification.title}</h3>
            <p className="mt-1 text-[13px] font-semibold text-slate-400">
              {notification.equipment}
              {notification.location ? ` · ${notification.location}` : ''}
            </p>
            <p className="mt-1 line-clamp-2 text-[13px] font-medium leading-5 text-slate-300">{notification.detail}</p>
            <p className="mt-2 text-[12px] font-medium text-slate-500">{notification.createdAt}</p>
          </div>
        </button>

        <button
          type="button"
          onClick={() => onDismiss(notification.id)}
          className="grid h-8 w-8 shrink-0 place-items-center rounded-lg border border-slate-700 text-slate-400 transition hover:border-red-400/70 hover:text-red-300"
          aria-label="알림 닫기"
        >
          <X className="h-4 w-4" />
        </button>
      </div>

      <button
        type="button"
        onClick={handleAnalyze}
        disabled={!canSearch}
        className="flex h-9 w-full items-center justify-center gap-2 rounded-lg bg-blue-600 text-[13px] font-black text-white transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:bg-slate-700"
      >
        <Search className="h-4 w-4" />
        {canSearch ? `분석 (${code})` : '분석 불가'}
      </button>
    </article>
  );
}
