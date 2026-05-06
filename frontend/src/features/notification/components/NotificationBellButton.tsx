import { useEffect, useRef, useState } from 'react';
import { Bell } from 'lucide-react';

import { notifications } from '../model/notificationData';
import { NotificationDropdown } from './NotificationDropdown';

export function NotificationBellButton() {
  const [isOpen, setIsOpen] = useState(false);
  const unreadCount = notifications.filter((notification) => notification.isUnread).length;
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!isOpen) return;
    const handleKeyDown = (event: KeyboardEvent) => {
  if (event.key === 'Escape') {
    setIsOpen(false);
  }
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
}, [isOpen]);


  return (
    <div ref={containerRef} className="relative">
      <button
        type="button"
        onClick={() => setIsOpen((prev) => !prev)}
        className="relative grid h-10 w-10 place-items-center rounded-xl text-slate-300 transition hover:bg-white/[0.04] hover:text-blue-300"
        aria-label="알림 열기"
      >
        <Bell className="h-7 w-7" />
        {unreadCount > 0 && (
          <span className="absolute -right-2 -top-2 grid h-6 w-6 place-items-center rounded-full bg-red-500 text-xs font-black text-white shadow-[0_0_16px_rgba(239,68,68,0.65)]">
            {unreadCount}
          </span>
        )}
      </button>

      {isOpen && <NotificationDropdown />}
    </div>
  );
}
