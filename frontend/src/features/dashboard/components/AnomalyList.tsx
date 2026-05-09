import { AlertTriangle, ChevronRight } from 'lucide-react';

import { Panel } from '../../../shared/ui/Panel';
import type { DashboardAnomalyDigest } from '../model/dashboard.types';
import { colorClasses, type DashboardColor } from '../model/dashboardTheme';

const LEVEL_COLOR: Record<DashboardAnomalyDigest['level'], DashboardColor> = {
  긴급: 'red',
  경고: 'amber',
  주의: 'slate',
};

function formatRelativeTime(iso: string): string {
  if (!iso) return '-';

  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return iso;

  const diffMs = Date.now() - date.getTime();
  const diffMin = Math.floor(diffMs / 60_000);

  if (diffMin < 1) return '방금 전';
  if (diffMin < 60) return `${diffMin}분 전`;

  const diffH = Math.floor(diffMin / 60);
  if (diffH < 24) return `${diffH}시간 전`;

  const diffD = Math.floor(diffH / 24);
  return `${diffD}일 전`;
}

type Props = {
  items: DashboardAnomalyDigest[];
};

export function AnomalyList({ items }: Props) {
  return (
    <Panel className="p-5 lg:col-span-5">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-[22px] font-extrabold">확인 필요 이상징후</h2>
        <ChevronRight className="h-7 w-7 text-slate-400" />
      </div>

      {items.length === 0 ? (
        <p className="py-8 text-center text-[14px] font-bold text-slate-500">미확인 이상징후가 없습니다.</p>
      ) : (
        <div className="divide-y divide-slate-700/70">
          {items.map((item) => {
            const palette = colorClasses[LEVEL_COLOR[item.level]];

            return (
              <article key={item.notificationId} className="grid grid-cols-[48px_minmax(0,1fr)_84px_120px_72px] items-center gap-5 py-5 first:pt-2">
                <div className={`grid h-12 w-12 place-items-center rounded-full ${palette.bg}`}>
                  <AlertTriangle className={`h-7 w-7 ${palette.text}`} />
                </div>
                <h3 className="truncate text-[19px] font-bold text-white">{item.title}</h3>
                <span className={`grid h-10 w-[64px] place-items-center rounded-md text-[17px] font-black ${palette.badge}`}>{item.level}</span>
                <span className="whitespace-nowrap text-[15px] font-medium text-slate-400">{item.meta}</span>
                <span className="whitespace-nowrap pr-[10px] text-right text-[15px] font-medium text-slate-400">{formatRelativeTime(item.occurredAt)}</span>
              </article>
            );
          })}
        </div>
      )}
    </Panel>
  );
}
