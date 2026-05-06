import { Link } from 'react-router-dom';
import { Lock, Mail, User } from 'lucide-react';

import { authScenarios } from '../model/authData';
import { AuthField } from './AuthField';
import { AuthShell } from './AuthShell';

export function SignupForm() {
  const scenario = authScenarios.signup;

  return (
    <AuthShell title={scenario.title} eyebrow={scenario.eyebrow} description={scenario.description}>
      <form className="space-y-3">
        <AuthField icon={User} label="이름" required placeholder="홍길동" />
        <AuthField icon={Mail} label="이메일" required type="email" placeholder="engineer@factory.com" />
        <AuthField icon={Lock} label="비밀번호 (8자 이상)" required type="password" placeholder="••••••••" />
        <AuthField label="소속" placeholder="라인A 보전팀" />

        <div className="flex items-center gap-6 py-2 text-[15px] font-semibold text-slate-300">
          <span className="text-slate-400">역할</span>
          <label className="flex items-center gap-2">
            <input type="radio" name="role" defaultChecked className="h-4 w-4 accent-blue-600" />
            작업자
          </label>
          <label className="flex items-center gap-2">
            <input type="radio" name="role" className="h-4 w-4 accent-blue-600" />
            관리자
          </label>
        </div>

        <button type="button" className="h-12 w-full rounded-lg bg-blue-600 text-[18px] font-black text-white shadow-[0_0_26px_rgba(37,99,235,0.35)] transition hover:bg-blue-500">
          {scenario.submitLabel}
        </button>
        <Link to={scenario.secondaryTo} className="grid h-11 w-full place-items-center rounded-lg border border-slate-700 bg-slate-950/20 text-[16px] font-bold text-slate-300 transition hover:border-blue-400/60 hover:text-blue-300">
          {scenario.secondaryLabel}
        </Link>
      </form>
    </AuthShell>
  );
}
