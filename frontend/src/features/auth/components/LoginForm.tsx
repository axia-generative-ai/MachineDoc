import { FormEvent, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Lock, Mail } from 'lucide-react';

import { useLogin } from '../hooks/useLogin';
import { authScenarios } from '../model/authData';
import { AuthField } from './AuthField';
import { AuthShell } from './AuthShell';

export function LoginForm() {
  const navigate = useNavigate();
  const scenario = authScenarios.login;
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const { login, isLoading, errorMessage } = useLogin({
    onSuccess: () => {
      navigate('/dashboard');
    },
  });

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    await login({ email: email.trim(), password });
  };

  return (
    <AuthShell title={scenario.title} eyebrow={scenario.eyebrow} description={scenario.description}>
      <form className="space-y-4" onSubmit={handleSubmit}>
        <AuthField
          icon={Mail}
          type="text"
          placeholder="engineer@factory.com"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          autoComplete="email"
        />
        <AuthField
          icon={Lock}
          type="password"
          placeholder="비밀번호"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          autoComplete="current-password"
        />

        {errorMessage && (
          <p className="rounded-lg border border-red-500/40 bg-red-500/10 px-4 py-3 text-[14px] font-bold text-red-300">
            {errorMessage}
          </p>
        )}

        <button
          type="submit"
          disabled={isLoading}
          className="h-12 w-full rounded-lg bg-blue-600 text-[18px] font-black text-white shadow-[0_0_26px_rgba(37,99,235,0.35)] transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:bg-slate-700 disabled:text-slate-400 disabled:shadow-none"
        >
          {isLoading ? '로그인 중...' : scenario.submitLabel}
        </button>
        <Link
          to={scenario.secondaryTo}
          className="grid h-11 w-full place-items-center rounded-lg border border-slate-700 bg-slate-950/20 text-[16px] font-bold text-slate-300 transition hover:border-blue-400/60 hover:text-blue-300"
        >
          {scenario.secondaryLabel}
        </Link>
      </form>
    </AuthShell>
  );
}
