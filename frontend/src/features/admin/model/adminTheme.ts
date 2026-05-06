export const adminStatColorClasses = {
  green: {
    text: 'text-emerald-400',
    bg: 'bg-emerald-500/10',
    icon: 'text-emerald-400',
  },
  red: {
    text: 'text-red-500',
    bg: 'bg-red-500/10',
    icon: 'text-red-500',
  },
} as const;

export type AdminStatColor = keyof typeof adminStatColorClasses;
