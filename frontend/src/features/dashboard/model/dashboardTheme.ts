export const colorClasses = {
  red: {
    text: 'text-red-500',
    bg: 'bg-red-500/10',
    ring: 'ring-red-500/20',
    badge: 'bg-red-600 text-white shadow-[0_0_20px_rgba(239,68,68,0.35)]',
  },
  amber: {
    text: 'text-amber-500',
    bg: 'bg-amber-500/10',
    ring: 'ring-amber-500/20',
    badge: 'bg-amber-500 text-white shadow-[0_0_20px_rgba(245,158,11,0.35)]',
  },
  green: {
    text: 'text-emerald-400',
    bg: 'bg-emerald-500/10',
    ring: 'ring-emerald-500/20',
    badge: 'bg-emerald-500 text-white',
  },
  blue: {
    text: 'text-blue-500',
    bg: 'bg-blue-500/10',
    ring: 'ring-blue-500/20',
    badge: 'bg-blue-500 text-white',
  },
  slate: {
    text: 'text-slate-300',
    bg: 'bg-slate-500/10',
    ring: 'ring-slate-500/20',
    badge: 'bg-slate-500 text-white shadow-[0_0_20px_rgba(148,163,184,0.22)]',
  },
} as const;

export type DashboardColor = keyof typeof colorClasses;
