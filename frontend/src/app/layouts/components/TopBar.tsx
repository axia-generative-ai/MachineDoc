import { useEffect, useRef, useState } from 'react';
import { ChevronDown, LogOut, Menu, Search, User } from 'lucide-react';

import { useAuthSession } from '../../../features/auth/hooks/useAuthSession';
import { useLogout } from '../../../features/auth/hooks/useLogout';
import { NotificationBellButton } from '../../../features/notification/components/NotificationBellButton';
import type { UserRole } from '../../../entities/user/model/user.types';

type TopBarProps = {
  isSidebarOpen: boolean;
  onMenuClick: () => void;
};

const roleLabels: Record<UserRole, string> = {
  ADMIN: '관리자',
  WORKER: '작업자',
  ENGINEER: '엔지니어',
};

function getRoleLabel(role?: UserRole) {
  if (!role) return '작업자';
  return roleLabels[role] ?? '작업자';
}

export function TopBar({ isSidebarOpen, onMenuClick }: TopBarProps) {
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);
  const userMenuRef = useRef<HTMLDivElement>(null);
  const { user } = useAuthSession();
  const { logout, isLoading } = useLogout();
  const userRoleLabel = getRoleLabel(user?.role);
  const userName = user?.name ?? '남궁현';
  const userDisplayName = `${userRoleLabel} ${userName}`;

  useEffect(() => {
    if (!isUserMenuOpen) return;

    const handleClickOutside = (event: MouseEvent) => {
      if (userMenuRef.current && !userMenuRef.current.contains(event.target as Node)) {
        setIsUserMenuOpen(false);
      }
    };

    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        setIsUserMenuOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    document.addEventListener('keydown', handleKeyDown);

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [isUserMenuOpen]);

  const handleLogout = async () => {
    setIsUserMenuOpen(false);
    await logout();
  };

  return (
    <header
      className={`fixed left-0 right-0 top-0 z-10 flex h-[78px] items-center border-b border-slate-800/90 bg-[#071018]/80 px-5 backdrop-blur-xl transition-[left] duration-300 ease-out lg:px-8 ${
        isSidebarOpen ? 'lg:left-[252px]' : 'lg:left-0'
      }`}
    >
      <button
        type="button"
        onClick={onMenuClick}
        className="mr-4 grid h-12 w-12 place-items-center rounded-xl border border-slate-700/60 bg-white/[0.03] text-slate-200 shadow-panel transition hover:border-blue-400/50 hover:text-blue-300"
        aria-label="사이드바 열기/닫기"
      >
        <Menu className="h-7 w-7" />
      </button>

      <label className="flex h-12 w-full max-w-[640px] items-center gap-3 rounded-lg border border-slate-600/80 bg-[#050b12]/80 px-4 text-slate-400 shadow-panel">
        <Search className="h-6 w-6 shrink-0" />
        <input
          className="w-full bg-transparent text-[18px] text-slate-200 outline-none placeholder:text-slate-400"
          placeholder="오류코드 또는 설비명을 입력하세요"
        />
      </label>

      <div className="ml-auto hidden items-center gap-6 text-[17px] font-semibold text-slate-100 xl:flex">
        <span className="flex items-center gap-2">
          <span className="h-3 w-3 rounded-full bg-emerald-400 shadow-[0_0_14px_rgba(52,211,153,0.7)]" />
          온라인
        </span>
        <span className="h-8 w-px bg-slate-700" />

        <div ref={userMenuRef} className="relative">
          <button
            type="button"
            onClick={() => setIsUserMenuOpen((prev) => !prev)}
            className="flex items-center gap-2 rounded-xl px-3 py-2 text-slate-100 transition hover:bg-white/[0.04] hover:text-blue-300"
            aria-haspopup="menu"
            aria-expanded={isUserMenuOpen}
          >
            <User className="h-7 w-7 text-slate-300" />
            <span>{userDisplayName}</span>
            <ChevronDown className={`h-5 w-5 text-slate-400 transition ${isUserMenuOpen ? 'rotate-180' : ''}`} />
          </button>

          {isUserMenuOpen && (
            <div className="absolute right-0 top-[52px] w-60 overflow-hidden rounded-2xl border border-slate-700/80 bg-[#08131f]/95 p-2 shadow-[0_22px_60px_rgba(0,0,0,0.45)] backdrop-blur-xl">
              <div className="border-b border-slate-700/70 px-3 py-3">
                <p className="text-sm font-bold text-slate-100">{userDisplayName}</p>
                <p className="mt-1 truncate text-xs font-medium text-slate-500">
                  {user?.email ?? 'FactoryGuard Operator'}
                </p>
              </div>
              <button
                type="button"
                onClick={handleLogout}
                disabled={isLoading}
                className="mt-2 flex w-full items-center gap-3 rounded-xl px-3 py-3 text-left text-sm font-bold text-red-300 transition hover:bg-red-500/10 hover:text-red-200 disabled:cursor-not-allowed disabled:text-slate-500"
                role="menuitem"
              >
                <LogOut className="h-5 w-5" />
                {isLoading ? '로그아웃 중...' : '로그아웃'}
              </button>
            </div>
          )}
        </div>

        <span className="h-8 w-px bg-slate-700" />
        <NotificationBellButton />
      </div>
    </header>
  );
}
