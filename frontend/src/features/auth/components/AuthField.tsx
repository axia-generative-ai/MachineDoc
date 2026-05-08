import type { InputHTMLAttributes } from 'react';
import type { LucideIcon } from 'lucide-react';

type AuthFieldProps = {
  label?: string;
  icon?: LucideIcon;
  required?: boolean;
} & InputHTMLAttributes<HTMLInputElement>;

export function AuthField({ label, icon: Icon, required, className = '', ...inputProps }: AuthFieldProps) {
  return (
    <label className="block">
      {label && (
        <span className={`mb-2 block text-[14px] font-bold ${required ? 'text-red-400' : 'text-slate-400'}`}>
          {label}
          {required ? ' *' : ''}
        </span>
      )}
      <div className="flex h-12 items-center gap-3 rounded-lg border border-slate-700/90 bg-slate-950/45 px-4 text-slate-400 transition focus-within:border-blue-400/70 focus-within:shadow-[0_0_20px_rgba(59,130,246,0.18)]">
        {Icon && <Icon className="h-5 w-5 shrink-0" />}
        <input className={`h-full flex-1 bg-transparent text-[16px] font-semibold text-white outline-none placeholder:text-slate-500 ${className}`} {...inputProps} />
      </div>
    </label>
  );
}
