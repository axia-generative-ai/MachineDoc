import { FormEvent, useState } from 'react';
import { Link } from 'react-router-dom';
import { Lock, Mail, User } from 'lucide-react';

import type { SignupCommand } from '../model/auth.types';
import { useSignup } from '../hooks/useSignup';
import { authScenarios } from '../model/authData';
import { AuthField } from './AuthField';
import { AuthShell } from './AuthShell';

const departments = ['라인A 보전팀', '라인B 보전팀', '라인C 보전팀'] as const;
const roles: Array<{ label: string; value: SignupCommand['role'] }> = [
  { label: '작업자', value: 'WORKER' },
  { label: '엔지니어', value: 'ENGINEER' },
];

export function SignupForm() {
  const scenario = authScenarios.signup;
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [department, setDepartment] = useState<(typeof departments)[number]>('라인A 보전팀');
  const [role, setRole] = useState<SignupCommand['role']>('WORKER');
  const { signup, isLoading, errorMessage, successMessage } = useSignup();

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    await signup({
      name: name.trim(),
      email: email.trim(),
      password,
      department,
      role,
    });
  };

  return (
    <AuthShell title={scenario.title} eyebrow={scenario.eyebrow} description={scenario.description}>
      <form className="space-y-3" onSubmit={handleSubmit}>
        <AuthField
          icon={User}
          label="이름"
          required
          placeholder="홍길동"
          value={name}
          onChange={(event) => setName(event.target.value)}
          autoComplete="name"
        />
        <AuthField
          icon={Mail}
          label="이메일"
          required
          type="email"
          placeholder="engineer@factory.com"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          autoComplete="email"
        />
        <AuthField
          icon={Lock}
          label="비밀번호 (8자 이상)"
          required
          type="password"
          placeholder="비밀번호"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          autoComplete="new-password"
        />

        <label className="block">
          <span className="mb-2 block text-[14px] font-bold text-red-400">소속 *</span>
          <select
            value={department}
            onChange={(event) => setDepartment(event.target.value as (typeof departments)[number])}
            className="h-12 w-full rounded-lg border border-slate-700/90 bg-slate-950/45 px-4 text-[16px] font-semibold text-white outline-none transition focus:border-blue-400/70 focus:shadow-[0_0_20px_rgba(59,130,246,0.18)]"
          >
            {departments.map((item) => (
              <option key={item} value={item} className="bg-slate-950 text-white">
                {item}
              </option>
            ))}
          </select>
        </label>

        <div className="py-2">
          <span className="mb-2 block text-[14px] font-bold text-slate-400">역할</span>
          <div className="grid grid-cols-2 gap-3">
            {roles.map((item) => (
              <label
                key={item.value}
                className={`flex h-11 cursor-pointer items-center justify-center gap-2 rounded-lg border text-[15px] font-bold transition ${
                  role === item.value
                    ? 'border-blue-400 bg-blue-500/15 text-blue-200'
                    : 'border-slate-700 bg-slate-950/30 text-slate-400 hover:border-blue-400/50 hover:text-blue-300'
                }`}
              >
                <input
                  type="radio"
                  name="role"
                  value={item.value}
                  checked={role === item.value}
                  onChange={() => setRole(item.value)}
                  className="h-4 w-4 accent-blue-600"
                />
                {item.label}
              </label>
            ))}
          </div>
          <p className="mt-2 text-xs font-medium text-slate-500">관리자 계정은 웹에서 가입할 수 없습니다.</p>
        </div>

        {(errorMessage || successMessage) && (
          <p
            className={`rounded-lg border px-4 py-3 text-[14px] font-bold ${
              successMessage
                ? 'border-emerald-500/40 bg-emerald-500/10 text-emerald-300'
                : 'border-red-500/40 bg-red-500/10 text-red-300'
            }`}
          >
            {successMessage ?? errorMessage}
          </p>
        )}

        <button
          type="submit"
          disabled={isLoading}
          className="h-12 w-full rounded-lg bg-blue-600 text-[18px] font-black text-white shadow-[0_0_26px_rgba(37,99,235,0.35)] transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:bg-slate-700 disabled:text-slate-400 disabled:shadow-none"
        >
          {isLoading ? '가입 요청 중...' : scenario.submitLabel}
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
