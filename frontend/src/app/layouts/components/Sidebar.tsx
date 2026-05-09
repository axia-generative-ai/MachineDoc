import type { LucideIcon } from 'lucide-react';
import { Activity, ClipboardCheck, FileText, Folder, History, Home, Search, Settings, ShieldCheck, User } from 'lucide-react';
import { Link, NavLink } from 'react-router-dom';

import type { UserRole } from '../../../entities/user/model/user.types';
import { useAuthSession } from '../../../features/auth/hooks/useAuthSession';

type SidebarProps = {
  isOpen: boolean;
};

type SidebarItem = {
  to: string;
  label: string;
  icon: LucideIcon;
  accent: 'blue' | 'emerald' | 'amber' | 'red' | 'violet' | 'slate';
  allowedRoles?: UserRole[];
};

type SidebarGroup = {
  title: string;
  items: SidebarItem[];
};

const primaryItems: SidebarItem[] = [
  { to: '/dashboard', label: '대시보드', icon: Home, accent: 'blue' },
  { to: '/error-search', label: '오류 검색', icon: Search, accent: 'violet' },
  { to: '/detection', label: '이상 감지', icon: Activity, accent: 'red' },
];

const groupedItems: SidebarGroup[] = [
  {
    title: 'MONITOR',
    items: [{ to: '/alert-log', label: '알림 로그', icon: FileText, accent: 'amber' }],
  },
  {
    title: 'HISTORY',
    items: [
      { to: '/search-history', label: '검색 이력', icon: History, accent: 'blue' },
      { to: '/action-history', label: '조치 이력', icon: ClipboardCheck, accent: 'emerald' },
      { to: '/saved-documents', label: '저장 문서', icon: Folder, accent: 'slate' },
    ],
  },
  {
    title: 'ADMIN',
    items: [{ to: '/admin', label: '관리자', icon: User, accent: 'red', allowedRoles: ['ADMIN'] }],
  },
  {
    title: 'ACCOUNT',
    items: [{ to: '/settings', label: '설정', icon: Settings, accent: 'emerald' }],
  },
];

const activeClasses: Record<SidebarItem['accent'], string> = {
  blue: 'bg-blue-500/15 text-blue-400 shadow-glow light:bg-blue-100 light:text-blue-700 light:ring-1 light:ring-blue-300/70',
  emerald: 'bg-emerald-500/15 text-emerald-300 shadow-[0_0_28px_rgba(16,185,129,0.2)] light:bg-emerald-100 light:text-emerald-700 light:ring-1 light:ring-emerald-300/70',
  amber: 'bg-amber-500/15 text-amber-300 shadow-[0_0_28px_rgba(245,158,11,0.18)] light:bg-amber-100 light:text-amber-700 light:ring-1 light:ring-amber-300/70',
  red: 'bg-red-500/15 text-red-300 shadow-[0_0_28px_rgba(239,68,68,0.18)] light:bg-red-100 light:text-red-700 light:ring-1 light:ring-red-300/70',
  violet: 'bg-violet-500/15 text-violet-300 shadow-[0_0_28px_rgba(139,92,246,0.18)] light:bg-violet-100 light:text-violet-700 light:ring-1 light:ring-violet-300/70',
  slate: 'bg-slate-500/15 text-slate-200 shadow-[0_0_24px_rgba(148,163,184,0.16)] light:bg-slate-200 light:text-slate-700 light:ring-1 light:ring-slate-300/80',
};

function SidebarLink({ to, label, icon: Icon, accent }: SidebarItem) {
  return (
    <NavLink
      to={to}
      end={to === '/'}
      className={({ isActive }) =>
        `group flex h-11 items-center gap-3 rounded-lg px-4 text-[16px] transition ${
          isActive ? activeClasses[accent] : 'text-slate-300 hover:bg-white/[0.04] hover:text-white light:hover:bg-slate-200/70 light:hover:text-slate-950'
        }`
      }
    >
      <Icon className="h-5 w-5 shrink-0" strokeWidth={2.1} />
      <span className="font-semibold">{label}</span>
    </NavLink>
  );
}

function canShowItem(item: SidebarItem, role?: UserRole) {
  if (!item.allowedRoles) return true;
  if (!role) return false;
  return item.allowedRoles.includes(role);
}

export function Sidebar({ isOpen }: SidebarProps) {
  const { user } = useAuthSession();

  const visibleGroups = groupedItems
    .map((group) => ({
      ...group,
      items: group.items.filter((item) => canShowItem(item, user?.role)),
    }))
    .filter((group) => group.items.length > 0);

  return (
    <aside
      className={`fixed inset-y-0 left-0 z-20 w-[78vw] max-w-[320px] border-r border-slate-700/70 bg-[#071018]/95 px-4 py-7 shadow-2xl shadow-black/40 backdrop-blur-xl transition-transform duration-300 ease-out lg:w-[252px] lg:max-w-none ${
        isOpen ? 'translate-x-0' : '-translate-x-full'
      }`}
    >
      <Link to="/dashboard" className="mb-10 flex items-center gap-2 px-1 text-blue-400">
        <ShieldCheck className="h-8 w-8 fill-blue-500/20" strokeWidth={2.6} />
        <span className="text-[23px] font-extrabold">FACTORYGUARD</span>
      </Link>

      <nav className="space-y-2">
        {primaryItems.map((item) => (
          <SidebarLink key={item.to} {...item} />
        ))}
      </nav>

      <div className="mt-6 space-y-6">
        {visibleGroups.map((group) => (
          <section key={group.title}>
            <div className="mb-2 flex items-center gap-3 px-1 text-[13px] font-semibold text-slate-400">
              <span>{group.title}</span>
              <span className="h-px flex-1 bg-slate-700/70" />
            </div>
            <div className="space-y-2">
              {group.items.map((item) => (
                <SidebarLink key={`${group.title}-${item.label}`} {...item} />
              ))}
            </div>
          </section>
        ))}
      </div>
    </aside>
  );
}
