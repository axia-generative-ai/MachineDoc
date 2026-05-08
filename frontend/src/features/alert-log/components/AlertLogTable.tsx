import { alertLogRows } from '../model/alertLogData';
import { Panel } from '../../../shared/ui/Panel';
import { AlertBadge } from './AlertBadge';
import { SortableHeader } from './SortableHeader';

export function AlertLogTable() {
  return (
    <Panel className="overflow-x-auto px-5 py-4">
      <div className="min-w-[980px]">
        <div className="grid grid-cols-[130px_160px_190px_1fr_150px] items-center border-b border-slate-700/80 px-7 py-5 text-[20px] font-black tracking-[-0.04em] text-slate-300">
          <SortableHeader label="시각" />
          <SortableHeader label="등급" align="center" />
          <SortableHeader label="설비" align="center" />
          <SortableHeader label="내용" />
          <SortableHeader label="상태" align="center" />
        </div>

        <div className="divide-y divide-slate-800/90">
          {alertLogRows.map((row) => (
            <article key={`${row.time}-${row.equipment}-${row.message}`} className="grid grid-cols-[130px_160px_190px_1fr_150px] items-center px-7 py-5 text-[20px] font-semibold tracking-[-0.04em] text-slate-200">
              <span>{row.time}</span>
              <span className="text-center">
                <AlertBadge type="severity" value={row.severity} />
              </span>
              <span className="text-center">{row.equipment}</span>
              <span>{row.message}</span>
              <span className="text-center">
                <AlertBadge type="status" value={row.status} />
              </span>
            </article>
          ))}
        </div>
      </div>
    </Panel>
  );
}
