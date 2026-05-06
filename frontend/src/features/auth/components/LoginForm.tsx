import { Link, useNavigate } from 'react-router-dom';
import { Lock, Mail } from 'lucide-react';

import { authScenarios } from '../model/authData';
import { AuthField } from './AuthField';
import { AuthShell } from './AuthShell';

export function LoginForm() {
  const navigate = useNavigate();
  const scenario = authScenarios.login;

  const handleLogin = () => {
    navigate('/dashboard');
  };

  return (
    <AuthShell title={scenario.title} eyebrow={scenario.eyebrow} description={scenario.description}>
      <form className="space-y-4">
        <AuthField icon={Mail} type="email" placeholder="engineer@factory.com" />
        <AuthField icon={Lock} type="password" placeholder="••••••••" />

        <button
          type="button"
          onClick={handleLogin}
          className="h-12 w-full rounded-lg bg-blue-600 text-[18px] font-black text-white shadow-[0_0_26px_rgba(37,99,235,0.35)] transition hover:bg-blue-500"
        >
          {scenario.submitLabel}
        </button>
        <Link to={scenario.secondaryTo} className="grid h-11 w-full place-items-center rounded-lg border border-slate-700 bg-slate-950/20 text-[16px] font-bold text-slate-300 transition hover:border-blue-400/60 hover:text-blue-300">
          {scenario.secondaryLabel}
        </Link>
      </form>
    </AuthShell>
  );
}
