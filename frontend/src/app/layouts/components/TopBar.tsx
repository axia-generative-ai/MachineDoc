import { Bell, Menu, Search, User } from 'lucide-react';

type TopBarProps = {
  isSidebarOpen: boolean;
  onMenuClick: () => void;
};

export function TopBar({ isSidebarOpen, onMenuClick }: TopBarProps) {
  return (
    <header
      className={`fixed left-0 right-0 top-0 z-10 flex h-[78px] items-center border-b border-slate-800/90 bg-[#071018]/80 px-5 backdrop-blur-xl transition-[left] duration-300 ease-out lg:px-8 ${
        isSidebarOpen ? 'lg:left-[252px]' : 'lg:left-0'
      }`}
    >
      {/* 버튼은 클릭만 상위로 전달하고, 실제 사이드바 열림 여부는 MainLayout에서 결정합니다. */}
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
        <span className="flex items-center gap-2">
          <User className="h-7 w-7 text-slate-300" />
          작업자 남궁현
        </span>
        <span className="h-8 w-px bg-slate-700" />
        <span className="relative">
          <Bell className="h-7 w-7 text-slate-300" />
          <span className="absolute -right-3 -top-3 grid h-6 w-6 place-items-center rounded-full bg-red-500 text-xs font-black text-white">3</span>
        </span>
      </div>
    </header>
  );
}
