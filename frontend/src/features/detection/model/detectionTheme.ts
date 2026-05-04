export const detectionColorClasses = {
  red: {
    text: 'text-red-500',
    bg: 'bg-red-500/10',
    icon: 'text-red-500',
  },
  blue: {
    text: 'text-white',
    bg: 'bg-blue-500/10',
    icon: 'text-blue-500',
  },
  amber: {
    text: 'text-white',
    bg: 'bg-amber-500/10',
    icon: 'text-orange-500',
  },
  green: {
    text: 'text-emerald-400',
    bg: 'bg-emerald-500/10',
    icon: 'text-emerald-400',
  },
} as const;

export type DetectionColor = keyof typeof detectionColorClasses;
