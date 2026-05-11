import { Download, Save } from 'lucide-react';

import type { AlertLogItem } from '../infra/alertLog.api';
import { alertFilters } from '../model/alertLogData';

type AlertLogHeaderProps = {
  selectedFilter: (typeof alertFilters)[number];
  onFilterChange: (filter: (typeof alertFilters)[number]) => void;
  items: AlertLogItem[];
};

function downloadFile(filename: string, content: string, mime: string) {
  const blob = new Blob([content], { type: mime });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

function timestampForFile() {
  const d = new Date();
  const pad = (n: number) => String(n).padStart(2, '0');
  return `${d.getFullYear()}${pad(d.getMonth() + 1)}${pad(d.getDate())}_${pad(d.getHours())}${pad(d.getMinutes())}`;
}

function csvEscape(value: string | number): string {
  const s = String(value ?? '');
  if (/[",\n]/.test(s)) return `"${s.replace(/"/g, '""')}"`;
  return s;
}

export function AlertLogHeader({ selectedFilter, onFilterChange, items }: AlertLogHeaderProps) {
  const handleSaveJson = () => {
    const payload = {
      exportedAt: new Date().toISOString(),
      filter: selectedFilter,
      total: items.length,
      items,
    };
    downloadFile(
      `alert-log_${timestampForFile()}.json`,
      JSON.stringify(payload, null, 2),
      'application/json',
    );
  };

  const handleExportCsv = () => {
    const header = ['시각', '등급', '설비코드', '위치', '내용', '상태'];
    const rows = items.map((item) => [
      item.occurredAt,
      item.level,
      item.equipmentCode,
      item.location,
      item.message,
      item.isRead,
    ]);
    const bom = '﻿'; // Excel 한글 깨짐 방지
    const csv = bom + [header, ...rows].map((row) => row.map(csvEscape).join(',')).join('\r\n');
    downloadFile(`alert-log_${timestampForFile()}.csv`, csv, 'text/csv;charset=utf-8');
  };

  return (
    <div className="mb-6">
      <h1 className="text-[40px] font-black tracking-[-0.06em] text-white">알림 로그</h1>

      <div className="mt-6 flex flex-col gap-4 xl:flex-row xl:items-center xl:justify-between">
        <div className="flex flex-wrap gap-3">
          {alertFilters.map((filter) => {
            const isActive = filter === selectedFilter;

            return (
              <button
                key={filter}
                type="button"
                onClick={() => onFilterChange(filter)}
                className={`h-[52px] min-w-[92px] rounded-lg border px-6 text-[20px] font-black tracking-[-0.04em] transition ${isActive
                    ? 'border-blue-500 bg-blue-600 text-white shadow-[0_0_24px_rgba(37,99,235,0.35)]'
                    : 'border-slate-700 bg-slate-950/25 text-slate-200 hover:border-blue-400/50 hover:text-blue-300'
                  }`}
              >
                {filter}
              </button>
            );
          })}
        </div>

        <div className="flex flex-wrap gap-3">
          <button
            type="button"
            onClick={handleSaveJson}
            disabled={items.length === 0}
            className="flex h-[52px] items-center gap-3 rounded-lg border border-blue-500 bg-blue-500/5 px-7 text-[19px] font-black tracking-[-0.04em] text-blue-400 transition hover:bg-blue-500/15 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Save className="h-6 w-6" />
            저장 (JSON)
          </button>
          <button
            type="button"
            onClick={handleExportCsv}
            disabled={items.length === 0}
            className="flex h-[52px] items-center gap-3 rounded-lg border border-blue-600 bg-blue-600 px-7 text-[19px] font-black tracking-[-0.04em] text-white shadow-[0_0_26px_rgba(37,99,235,0.35)] transition hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Download className="h-6 w-6" />
            저장 (CSV)
          </button>
        </div>
      </div>
    </div>
  );
}
