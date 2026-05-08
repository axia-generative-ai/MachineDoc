import { notifications } from '../model/notificationData';
import { NotificationItem } from './NotificationItem';

export function NotificationDropdown() {
  return (
    <section className="absolute right-0 top-[54px] z-30 w-[380px] overflow-hidden rounded-2xl border border-slate-700/80 bg-[#071018]/95 shadow-[0_24px_80px_rgba(0,0,0,0.55)] backdrop-blur-xl">
      <div className="flex items-center justify-between border-b border-slate-700/80 bg-red-500/95 px-4 py-3 text-white">
        <div className="flex items-center gap-2">
          <span className="h-3 w-3 rounded-full bg-white" />
          <h2 className="text-[15px] font-black tracking-[-0.04em]">실시간 알림</h2>
        </div>
        <span className="text-[13px] font-bold">현재 {notifications.length}건</span>
      </div>

      <div className="max-h-[440px] space-y-3 overflow-y-auto p-3">
        {notifications.map((notification) => (
          <NotificationItem key={notification.id} notification={notification} />
        ))}
      </div>
    </section>
  );
}
