import { useEffect, useRef, useState } from 'react';
import { Bell } from 'lucide-react';

import { useNotificationSocket } from '../hooks/useNotificationSocket';
import { NotificationDropdown } from './NotificationDropdown';

export function NotificationBellButton() {
  const [isOpen, setIsOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const { notifications, unreadCount, status, markAllRead, dismissNotification, clearNotifications } = useNotificationSocket();

  useEffect(() => {
    if (!isOpen) return;

    markAllRead();

    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') setIsOpen(false);
    };

    const handleClickOutside = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    document.addEventListener('keydown', handleKeyDown);

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [isOpen, markAllRead]);

  return (
    <div ref={containerRef} className="relative">
      <button
        type="button"
        onClick={() => setIsOpen((prev) => !prev)}
        className="relative grid h-10 w-10 place-items-center rounded-xl text-slate-300 transition hover:bg-white/[0.04] hover:text-blue-300"
        aria-label="알림 열기"
      >
        <Bell className="h-7 w-7" />
        {status === 'connected' && <span className="absolute right-1 top-1 h-2.5 w-2.5 rounded-full bg-emerald-400 shadow-[0_0_10px_rgba(52,211,153,0.8)]" />}
        {unreadCount > 0 && (
          <span className="absolute -right-2 -top-2 grid h-6 min-w-6 place-items-center rounded-full bg-red-500 px-1.5 text-xs font-black text-white shadow-[0_0_16px_rgba(239,68,68,0.65)]">
            {unreadCount > 9 ? '9+' : unreadCount}
          </span>
        )}
      </button>

      {isOpen && (
        <NotificationDropdown
          notifications={notifications}
          status={status}
          onDismiss={dismissNotification}
          onClear={clearNotifications}
          onClose={() => setIsOpen(false)}
        />
      )}
    </div>
  );
}
