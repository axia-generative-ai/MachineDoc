import { useNotifications } from '../providers/NotificationsProvider';
import { NotificationItem } from './NotificationItem';

type Props = {
  onClose: () => void;
};

export function NotificationDropdown({ onClose }: Props) {
  const { notifications, isConnected, clear } = useNotifications();

  return (
    <section className="absolute right-0 top-[54px] z-30 w-[380px] overflow-hidden rounded-2xl border border-slate-700/80 bg-[#071018]/95 shadow-[0_24px_80px_rgba(0,0,0,0.55)] backdrop-blur-xl">
      <div className="flex items-center justify-between border-b border-slate-700/80 bg-red-500/95 px-4 py-3 text-white">
        <div className="flex items-center gap-2">
          <span className={`h-3 w-3 rounded-full ${isConnected ? 'bg-white' : 'bg-white/40'}`} />
          <h2 className="text-[15px] font-black tracking-[-0.04em]">실시간 알림 {isConnected ? '' : '(연결 끊김)'}</h2>
        </div>
        <span className="text-[13px] font-bold">현재 {notifications.length}건</span>
      </div>

      {notifications.length === 0 ? (
        <p className="px-5 py-8 text-center text-[14px] font-bold text-slate-400">새 알림이 없습니다.</p>
      ) : (
        <>
          <div className="max-h-[440px] space-y-3 overflow-y-auto p-3">
            {notifications.map((notification) => (
              <NotificationItem key={notification.id} notification={notification} onNavigate={onClose} />
            ))}
          </div>
          <button
            type="button"
            onClick={clear}
            className="w-full border-t border-slate-700/80 px-4 py-3 text-[13px] font-black text-slate-300 transition hover:bg-slate-800/40"
          >
            모두 지우기
          </button>
        </>
      )}
    </section>
  );
}
