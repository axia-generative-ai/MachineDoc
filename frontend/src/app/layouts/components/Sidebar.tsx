import type { LucideIcon } from 'lucide-react';
import { Link, NavLink } from 'react-router-dom';
import { Activity, Bell, ClipboardCheck, FileText, Folder, History, Home, Search, Settings, ShieldCheck, User } from 'lucide-react';

type SidebarProps = {
  isOpen: boolean;
};

const primaryItems = [
  { to: '/dashboard', label: '대시보드', icon: Home },
  { to: '/error-search', label: '오류 검색', icon: Search },
  { to: '/detection', label: '이상감지', icon: Activity },
];

const groupedItems = [
  {
    title: 'MONITOR',
    items: [
      { to: '/alert-log', label: '알림 로그', icon: FileText },
    ],
  },
  {
    title: 'HISTORY',
    items: [
      { to: '/search-history', label: '검색 이력', icon: History },
      { to: '/action-history', label: '조치 이력', icon: ClipboardCheck },
      { to: '/saved-documents', label: '저장 문서', icon: Folder },
    ],
  },
  {
    title: 'ADMIN',
    items: [{ to: '/admin', label: '관리자', icon: User }],
  },
  {
    title: 'ACCOUNT',
    items: [{ to: '/settings', label: '설정', icon: Settings }],
  },
];

function SidebarLink({ to, label, icon: Icon }: { to: string; label: string; icon: LucideIcon }) {
  return (
    <NavLink
      to={to}
      end={to === '/'}
      className={({ isActive }) =>
        `group flex h-11 items-center gap-3 rounded-lg px-4 text-[16px] transition ${
          isActive
            ? 'bg-blue-500/15 text-blue-400 shadow-glow'
            : 'text-slate-300 hover:bg-white/[0.04] hover:text-white'
        }`
      }
    >
      <Icon className="h-5 w-5 shrink-0" strokeWidth={2.1} />
      <span className="font-semibold tracking-[-0.03em]">{label}</span>
    </NavLink>
  );
}

export function Sidebar({ isOpen }: SidebarProps) {
  return (
    <aside
      // 모바일은 overlay drawer, 데스크톱은 고정 sidebar처럼 동작합니다.
      className={`fixed inset-y-0 left-0 z-20 w-[78vw] max-w-[320px] border-r border-slate-700/70 bg-[#071018]/95 px-4 py-7 shadow-2xl shadow-black/40 backdrop-blur-xl transition-transform duration-300 ease-out lg:w-[252px] lg:max-w-none ${
        isOpen ? 'translate-x-0' : '-translate-x-full'
      }`}
    >
      <Link to="/" className="mb-10 flex items-center gap-2 px-1 text-blue-400">
        <ShieldCheck className="h-8 w-8 fill-blue-500/20" strokeWidth={2.6} />
        <span className="text-[23px] font-extrabold tracking-[-0.05em]">FACTORYGUARD</span>
      </Link>

      <nav className="space-y-2">
        {primaryItems.map((item) => (
          <SidebarLink key={item.to} {...item} />
        ))}
      </nav>

      <div className="mt-6 space-y-6">
        {groupedItems.map((group) => (
          <section key={group.title}>
            <div className="mb-2 flex items-center gap-3 px-1 text-[13px] font-semibold text-slate-400">
              <span>{group.title}</span>
              <span className="h-px flex-1 bg-slate-700/70" />
            </div>
            <div className="space-y-2">
              {group.items.map((item) => (
                <SidebarLink key={item.to} {...item} />
              ))}
            </div>
          </section>
        ))}
      </div>
    </aside>
  );
}
