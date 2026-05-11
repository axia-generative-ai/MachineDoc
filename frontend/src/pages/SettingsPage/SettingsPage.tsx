import { Bell, Check, Moon, Palette, ShieldCheck, Sun, UserRound } from 'lucide-react';

import { useAuthSession } from '../../features/auth/hooks/useAuthSession';
import type { UserRole } from '../../entities/user/model/user.types';
import { useThemePreference, type ThemePreference } from '../../shared/theme/themePreference';
import { Panel } from '../../shared/ui/Panel';

const roleLabels: Record<UserRole, string> = {
  ADMIN: '관리자',
  ENGINEER: '엔지니어',
  WORKER: '작업자',
};

const themeOptions: Array<{
  value: ThemePreference;
  label: string;
  description: string;
  icon: typeof Moon;
}> = [
  {
    value: 'dark',
    label: '다크 모드',
    description: '관제실 환경에 맞춘 고대비 화면',
    icon: Moon,
  },
  {
    value: 'light',
    label: '라이트 모드',
    description: '밝은 작업 공간에서 보기 편한 화면',
    icon: Sun,
  },
];

export function SettingsPage() {
  const { user } = useAuthSession();
  const { theme, setTheme } = useThemePreference();

  return (
    <div className="mx-auto max-w-[1320px]">
      <div className="mb-6 flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <p className="text-[13px] font-black uppercase tracking-[0.18em] text-blue-300">Account Control</p>
          <h1 className="mt-2 text-[40px] font-black text-white">설정</h1>
          <p className="mt-2 text-[16px] font-semibold text-slate-400">계정 표시 정보와 작업 화면 환경을 관리합니다.</p>
        </div>
        <div className="inline-flex h-11 w-fit items-center gap-2 rounded-lg border border-emerald-400/30 bg-emerald-500/10 px-4 text-[14px] font-black text-emerald-300">
          <ShieldCheck className="h-5 w-5" />
          보안 세션 활성
        </div>
      </div>

      <div className="grid gap-5 xl:grid-cols-[360px_minmax(0,1fr)]">
        <Panel className="p-6">
          <div className="flex items-center gap-4">
            <div className="grid h-16 w-16 place-items-center rounded-full border border-blue-400/30 bg-blue-500/10 text-blue-300">
              <UserRound className="h-8 w-8" />
            </div>
            <div className="min-w-0">
              <p className="truncate text-[22px] font-black text-white">{user?.name ?? '작업자'}</p>
              <p className="mt-1 truncate text-[14px] font-semibold text-slate-400">{user?.email ?? '로그인 정보 없음'}</p>
            </div>
          </div>

          <div className="mt-6 space-y-3 border-t border-slate-700/70 pt-5">
            <div className="flex items-center justify-between gap-4">
              <span className="text-[13px] font-bold text-slate-500">역할</span>
              <span className="text-[14px] font-black text-slate-100">{user?.role ? roleLabels[user.role] : '-'}</span>
            </div>
            <div className="flex items-center justify-between gap-4">
              <span className="text-[13px] font-bold text-slate-500">소속</span>
              <span className="truncate text-right text-[14px] font-black text-slate-100">{user?.department ?? '-'}</span>
            </div>
            <div className="flex items-center justify-between gap-4">
              <span className="text-[13px] font-bold text-slate-500">상태</span>
              <span className="rounded-md border border-emerald-400/35 bg-emerald-500/10 px-2.5 py-1 text-[12px] font-black text-emerald-300">접속 중</span>
            </div>
          </div>
        </Panel>

        <div className="space-y-5">
          <Panel className="p-6">
            <div className="mb-5 flex items-center justify-between gap-4">
              <div>
                <h2 className="flex items-center gap-3 text-[24px] font-black text-white">
                  <Palette className="h-6 w-6 text-blue-400" />
                  화면 모드
                </h2>
                <p className="mt-2 text-[14px] font-semibold text-slate-500">선택한 모드는 이 브라우저에 저장됩니다.</p>
              </div>
              <span className="rounded-md border border-slate-600/70 px-3 py-1.5 text-[12px] font-black text-slate-300">
                {theme === 'light' ? 'LIGHT' : 'DARK'}
              </span>
            </div>

            <div className="grid gap-3 md:grid-cols-2">
              {themeOptions.map((option) => {
                const Icon = option.icon;
                const isSelected = theme === option.value;

                return (
                  <button
                    key={option.value}
                    type="button"
                    onClick={() => setTheme(option.value)}
                    className={`flex min-h-[132px] items-start gap-4 rounded-xl border p-5 text-left transition ${
                      isSelected
                        ? 'border-blue-400/80 bg-blue-500/15 shadow-glow'
                        : 'border-slate-700/80 bg-slate-950/20 hover:border-blue-400/40 hover:bg-slate-900/45'
                    }`}
                  >
                    <span className={`grid h-11 w-11 shrink-0 place-items-center rounded-lg ${isSelected ? 'bg-blue-500 text-white' : 'bg-slate-800 text-slate-300'}`}>
                      <Icon className="h-6 w-6" />
                    </span>
                    <span className="min-w-0 flex-1">
                      <span className="flex items-center justify-between gap-3">
                        <span className="text-[18px] font-black text-white">{option.label}</span>
                        {isSelected && <Check className="h-5 w-5 shrink-0 text-blue-300" />}
                      </span>
                      <span className="mt-2 block text-[14px] font-semibold leading-6 text-slate-400">{option.description}</span>
                    </span>
                  </button>
                );
              })}
            </div>
          </Panel>

          <Panel className="p-6">
            <h2 className="flex items-center gap-3 text-[24px] font-black text-white">
              <Bell className="h-6 w-6 text-amber-400" />
              알림 환경
            </h2>
            <div className="mt-5 grid gap-3 md:grid-cols-3">
              {['실시간 이상 감지', '관리자 승인 이벤트', '오류 분석 결과'].map((label) => (
                <div key={label} className="flex h-14 items-center justify-between rounded-xl border border-slate-700/80 bg-slate-950/20 px-4">
                  <span className="text-[14px] font-bold text-slate-200">{label}</span>
                  <span className="rounded-full bg-emerald-500/15 px-2.5 py-1 text-[11px] font-black text-emerald-300">ON</span>
                </div>
              ))}
            </div>
          </Panel>
        </div>
      </div>
    </div>
  );
}
