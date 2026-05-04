import { LineChart } from 'lucide-react';

import { hourlyTrendData } from '../model/dashboardData';
import { Panel } from '../../../shared/ui/Panel';

export function TrendChart() {
  const chartHeight = 10;
  const xPadding = 0.5;
  const chartWidth = hourlyTrendData.length - 1 + xPadding * 2;
  const chartPoints = hourlyTrendData.map((item, index) => [index + xPadding, chartHeight - item.count]);
  const polyline = chartPoints.map(([x, y]) => `${x},${y}`).join(' ');

  return (
    <Panel className="p-5 lg:col-span-7">
      <div className="mb-5 flex items-center justify-between">
        <h2 className="text-[22px] font-extrabold tracking-[-0.04em]">오류 발생 추이 (24h)</h2>
        <LineChart className="h-7 w-7 text-slate-400" />
      </div>
      <div className="relative h-[315px] pl-10 pr-3 pt-1">
        <div className="absolute bottom-8 left-10 right-3 top-2 border-b-2 border-l-2 border-slate-400/60">
          {[0, 1, 2, 3, 4].map((line) => (
            <span
              key={line}
              className="absolute left-0 right-0 border-t border-dashed border-slate-600/60"
              style={{ top: `${line * 20}%` }}
            />
          ))}
          <svg className="absolute inset-0 h-full w-full overflow-visible" viewBox={`0 0 ${chartWidth} ${chartHeight}`} preserveAspectRatio="none">
            <polyline points={polyline} fill="none" stroke="#2f82ff" strokeWidth="1.8" vectorEffect="non-scaling-stroke" />
            {chartPoints.map(([x, y]) => (
              <circle
                key={`${x}-${y}`}
                cx={x}
                cy={y}
                r="0.1"
                fill="#2f82ff"
                stroke="#58a0ff"
                strokeWidth="1.5"
                vectorEffect="non-scaling-stroke"
              />
            ))}
          </svg>
        </div>
        <div className="absolute bottom-8 left-0 top-2 flex flex-col justify-between text-[16px] font-medium text-slate-200">
          {[10, 8, 6, 4, 2, 0].map((tick) => (
            <span key={tick}>{tick}</span>
          ))}
        </div>
        <div className="absolute bottom-0 left-10 right-3 grid grid-cols-12 text-center text-[16px] font-medium text-slate-200">
          {hourlyTrendData.map((item) => (
            <span key={item.hour}>{item.hour}</span>
          ))}
        </div>
      </div>
    </Panel>
  );
}
