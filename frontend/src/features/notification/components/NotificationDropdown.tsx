import type { NotificationSocketStatus, RealtimeNotification } from '../model/notification.types';
import { NotificationItem } from './NotificationItem';

type NotificationDropdownProps = {
  notifications: RealtimeNotification[];
  status: NotificationSocketStatus;
  onDismiss: (id: string) => void;
};

const statusLabels = {
  idle: '토큰 없음',
  connecting: '연결 중',
  connected: '실시간 연결',
  disconnected: '연결 종료',
  error: '연결 오류',
} as const;

export function NotificationDropdown({ notifications, status, onDismiss }: NotificationDropdownProps) {
  return (
    <section className="absolute right-0 top-[54px] z-30 w-[380px] overflow-hidden rounded-2xl border border-slate-700/80 bg-[#071018]/95 shadow-[0_24px_80px_rgba(0,0,0,0.55)] backdrop-blur-xl">
      <div className="flex items-center justify-between border-b border-slate-700/80 bg-red-500/95 px-4 py-3 text-white">
        <div className="flex items-center gap-2">
          <span className={`h-3 w-3 rounded-full ${status === 'connected' ? 'bg-emerald-200' : 'bg-white/70'}`} />
          <h2 className="text-[15px] font-black">실시간 알림</h2>
        </div>
        <span className="text-[13px] font-bold">
          {statusLabels[status]} · {notifications.length}건
        </span>
      </div>

      <div className="max-h-[440px] space-y-3 overflow-y-auto p-3">
        {notifications.length === 0 ? (
          <div className="rounded-xl border border-slate-700/70 bg-slate-950/40 px-4 py-8 text-center">
            <p className="text-[15px] font-bold text-slate-200">수신된 알림이 없습니다.</p>
            <p className="mt-2 text-[13px] font-medium text-slate-500">이상 징후가 발생하면 여기에 표시됩니다.</p>
          </div>
        ) : (
          notifications.map((notification) => <NotificationItem key={notification.id} notification={notification} onDismiss={onDismiss} />)
        )}
      </div>
    </section>
  );
}
