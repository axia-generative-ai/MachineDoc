import { ChevronsUpDown } from 'lucide-react';

type SortableHeaderProps = {
  label: string;
  align?: 'left' | 'center' | 'right';
};

export function SortableHeader({ label, align = 'left' }: SortableHeaderProps) {
  const alignClassName = {
    left: 'justify-start',
    center: 'justify-center',
    right: 'justify-end',
  }[align];

  return (
    <div className={`flex items-center gap-2 ${alignClassName}`}>
      <span>{label}</span>
      <ChevronsUpDown className="h-5 w-5 text-slate-500" />
    </div>
  );
}
