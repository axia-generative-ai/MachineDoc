import type { ReactNode } from 'react';

type PanelProps = {
  children: ReactNode;
  className?: string;
};

export function Panel({ children, className = '' }: PanelProps) {
  return (
    <section className={`rounded-2xl border border-slate-700/80 bg-slate-950/35 shadow-panel backdrop-blur-xl ${className}`}>
      {children}
    </section>
  );
}
