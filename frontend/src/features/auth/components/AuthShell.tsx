import type { ReactNode } from 'react';
import { ShieldCheck } from 'lucide-react';

import authHeroImage from '../../../assets/images/start.png';

type AuthShellProps = {
  children: ReactNode;
  title: string;
  eyebrow: string;
  description: string;
};

export function AuthShell({ children, title, eyebrow, description }: AuthShellProps) {
  return (
    <main className="relative min-h-screen overflow-hidden bg-[#03070b] text-slate-100">
      <img className="absolute inset-0 h-full w-full object-cover" src={authHeroImage} alt="MachineDoc smart factory control room" />
      <div className="absolute inset-0 bg-slate-950/45" />
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_45%,rgba(37,99,235,0.16),transparent_34%),linear-gradient(135deg,rgba(3,7,11,0.78),rgba(7,16,24,0.42),rgba(3,7,11,0.72))]" />

      <section className="relative z-10 flex min-h-screen items-center justify-center px-5 py-10">
        <div className="w-full max-w-[470px]">
          <div className="mb-7 flex justify-center">
            <div className="flex items-center gap-3 rounded-full border border-blue-400/25 bg-blue-500/10 px-5 py-3 text-blue-400 shadow-[0_0_34px_rgba(37,99,235,0.24)] backdrop-blur-xl">
              <ShieldCheck className="h-8 w-8 fill-blue-500/20" strokeWidth={2.5} />
              <span className="text-[24px] font-black tracking-[-0.06em]">{eyebrow}</span>
            </div>
          </div>

          <div className="rounded-3xl border border-slate-700/80 bg-slate-950/70 p-7 shadow-[0_28px_90px_rgba(0,0,0,0.55)] backdrop-blur-2xl sm:p-9">
            <p className="mb-3 text-center text-[14px] font-black tracking-[0.2em] text-blue-400">SECURE ACCESS</p>
            <h1 className="text-center text-[38px] font-black tracking-[-0.07em] text-white">{title}</h1>
            <p className="mt-3 text-center text-[16px] font-semibold tracking-[-0.04em] text-slate-400">{description}</p>

            <div className="mt-8">{children}</div>
          </div>
        </div>
      </section>
    </main>
  );
}
