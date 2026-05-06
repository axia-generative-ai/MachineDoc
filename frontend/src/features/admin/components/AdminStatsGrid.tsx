import { adminStats } from '../model/adminData';
import { adminStatColorClasses, type AdminStatColor } from '../model/adminTheme';

export function AdminStatsGrid() {
  return (
    <div className="grid gap-4 md:grid-cols-2">
      {adminStats.map((stat) => {
        const Icon = stat.icon;
        const palette = adminStatColorClasses[stat.color as AdminStatColor];

        return (
          <article key={stat.label} className="flex min-h-[120px] items-center justify-between rounded-xl border border-slate-700/80 bg-slate-950/20 p-5">
            <div>
              <p className={`text-[42px] font-black leading-none tracking-[-0.06em] ${palette.text}`}>
                {stat.value}
                <span className="ml-1 text-[20px]">{stat.unit}</span>
              </p>
              <p className="mt-3 text-[16px] font-bold text-slate-200">{stat.label}</p>
            </div>
            <div className={`grid h-16 w-16 place-items-center rounded-full ${palette.bg}`}>
              <Icon className={`h-9 w-9 ${palette.icon}`} />
            </div>
          </article>
        );
      })}
    </div>
  );
}
