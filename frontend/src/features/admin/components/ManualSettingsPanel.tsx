import { useEffect, useRef, useState } from 'react';
import { CheckCircle2, Loader2, Upload } from 'lucide-react';

import { Panel } from '../../../shared/ui/Panel';

const CATEGORY_OPTIONS = ['점검', '수리', '운전', '안전', '교체'] as const;

// 시드 순서 (backend/seeds/demo.sql)와 동일: 1:MOTOR, 2:CONVEYOR, 3:PRESS, 4:ROBOT, 5:WELDING
export const EQUIPMENT_OPTIONS = [
  { id: 1, label: '정밀 모터 (Line A) — EQ-MOTOR-001' },
  { id: 2, label: '표준 컨베이어 (Line A) — EQ-CONVEYOR-002' },
  { id: 3, label: '고온 프레스 (Line B) — EQ-PRESS-003' },
  { id: 4, label: '정밀 로봇 (Line B) — EQ-ROBOT-004' },
  { id: 5, label: '용접기 (Line C) — EQ-WELDING-005' },
] as const;

export type ManualUploadFormValues = {
  title: string;
  category: string;
  version: string;
  equipmentId: number | null;
  errorCodes: string;
  file: File | null;
};

type Props = {
  values: ManualUploadFormValues;
  onChange: (next: ManualUploadFormValues) => void;
  onSubmit: () => void;
  isSubmitting: boolean;
  errorMessage: string | null;
  successMessage: string | null;
};

const STAGE_LABELS = ['파일 업로드', 'PDF 청킹', '벡터 임베딩', 'DB 색인'] as const;
const STAGE_INTERVAL_MS = 4000;

export function ManualSettingsPanel({ values, onChange, onSubmit, isSubmitting, errorMessage, successMessage }: Props) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [elapsedSec, setElapsedSec] = useState(0);

  useEffect(() => {
    if (!isSubmitting) {
      setElapsedSec(0);
      return;
    }
    const start = Date.now();
    const timer = window.setInterval(() => {
      setElapsedSec(Math.floor((Date.now() - start) / 1000));
    }, 250);
    return () => window.clearInterval(timer);
  }, [isSubmitting]);

  const stageIndex = Math.min(STAGE_LABELS.length - 1, Math.floor((elapsedSec * 1000) / STAGE_INTERVAL_MS));

  const update = (patch: Partial<ManualUploadFormValues>) => onChange({ ...values, ...patch });

  return (
    <Panel className="relative p-6">
      <h2 className="text-[24px] font-black tracking-[-0.05em] text-white">매뉴얼 등록</h2>
      <p className="mt-1 text-[13px] font-semibold text-slate-400">
        PDF 매뉴얼을 업로드합니다. 이 매뉴얼이 다루는 오류코드를 함께 입력하면 작업자 검색에 즉시 매칭됩니다.
        등록된 매핑은 "오류코드 매핑" 탭에서 확인할 수 있습니다.
      </p>

      <form
        className="mt-6 space-y-5"
        onSubmit={(event) => {
          event.preventDefault();
          onSubmit();
        }}
      >
        <label className="block">
          <span className="mb-2 block text-[16px] font-semibold text-slate-400">매뉴얼명</span>
          <input
            className="h-12 w-full rounded-lg border border-slate-700 bg-slate-950/30 px-4 text-[18px] font-semibold text-white outline-none focus:border-blue-400/70"
            value={values.title}
            onChange={(event) => update({ title: event.target.value })}
            placeholder="예: YASKAWA GA700 모터 점검 매뉴얼"
            required
          />
        </label>

        <label className="block">
          <span className="mb-2 block text-[16px] font-semibold text-slate-400">카테고리</span>
          <select
            className="h-12 w-full rounded-lg border border-slate-700 bg-slate-950/30 px-4 text-[18px] font-semibold text-white outline-none focus:border-blue-400/70"
            value={values.category}
            onChange={(event) => update({ category: event.target.value })}
            required
          >
            {CATEGORY_OPTIONS.map((option) => (
              <option key={option} value={option} className="bg-slate-950 text-white">
                {option}
              </option>
            ))}
          </select>
        </label>

        <label className="block">
          <span className="mb-2 block text-[16px] font-semibold text-slate-400">
            대상 설비
            <span className="ml-1 text-[13px] font-normal text-slate-500">(선택 — 알림→매뉴얼 매칭에 사용)</span>
          </span>
          <select
            className="h-12 w-full rounded-lg border border-slate-700 bg-slate-950/30 px-4 text-[18px] font-semibold text-white outline-none focus:border-blue-400/70"
            value={values.equipmentId ?? ''}
            onChange={(event) => {
              const raw = event.target.value;
              update({ equipmentId: raw === '' ? null : Number(raw) });
            }}
          >
            <option value="" className="bg-slate-950 text-white">선택 안 함 (글로벌 매뉴얼)</option>
            {EQUIPMENT_OPTIONS.map((option) => (
              <option key={option.id} value={option.id} className="bg-slate-950 text-white">
                {option.label}
              </option>
            ))}
          </select>
        </label>

        <label className="block">
          <span className="mb-2 block text-[16px] font-semibold text-slate-400">버전</span>
          <input
            className="h-12 w-full rounded-lg border border-slate-700 bg-slate-950/30 px-4 text-[18px] font-semibold text-white outline-none focus:border-blue-400/70"
            value={values.version}
            onChange={(event) => update({ version: event.target.value })}
            placeholder="예: v1.0"
            required
          />
        </label>

        <label className="block">
          <span className="mb-2 block text-[16px] font-semibold text-slate-400">
            이 매뉴얼이 다루는 오류코드
            <span className="ml-1 text-[13px] font-normal text-slate-500">(쉼표 또는 공백으로 구분)</span>
          </span>
          <input
            className="h-12 w-full rounded-lg border border-slate-700 bg-slate-950/30 px-4 text-[18px] font-semibold text-white outline-none focus:border-blue-400/70"
            value={values.errorCodes}
            onChange={(event) => update({ errorCodes: event.target.value })}
            placeholder="예: E0099, E0098, E0097"
          />
          <p className="mt-1 text-[12px] font-medium text-slate-500">
            여기에 등록한 코드가 발생하면 이 매뉴얼이 자동으로 매칭됩니다.
            (입력하지 않아도 PDF에서 자동 추출된 코드가 매핑됩니다)
          </p>
        </label>

        <div>
          <span className="mb-2 block text-[16px] font-semibold text-slate-400">PDF 파일</span>
          <input
            ref={fileInputRef}
            type="file"
            accept="application/pdf"
            onChange={(event) => update({ file: event.target.files?.[0] ?? null })}
            className="block w-full cursor-pointer rounded-lg border border-slate-700 bg-slate-950/30 p-3 text-[15px] font-semibold text-slate-300 file:mr-4 file:rounded-md file:border-0 file:bg-blue-600 file:px-4 file:py-2 file:text-[14px] file:font-black file:text-white file:transition file:hover:bg-blue-500"
            required
          />
          {values.file && (
            <p className="mt-2 text-[13px] font-semibold text-slate-400">
              선택됨: {values.file.name} ({(values.file.size / 1024).toFixed(1)} KB)
            </p>
          )}
        </div>

        {errorMessage && (
          <p className="rounded-lg border border-red-500/40 bg-red-500/10 px-4 py-3 text-[14px] font-bold text-red-300">
            {errorMessage}
          </p>
        )}
        {successMessage && (
          <p className="rounded-lg border border-emerald-500/40 bg-emerald-500/10 px-4 py-3 text-[14px] font-bold text-emerald-300">
            {successMessage}
          </p>
        )}

        <button
          type="submit"
          disabled={isSubmitting}
          className="flex h-12 w-full items-center justify-center gap-2 rounded-lg bg-blue-600 text-[17px] font-black text-white shadow-[0_0_20px_rgba(37,99,235,0.35)] transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:bg-slate-700 disabled:text-slate-400 disabled:shadow-none"
        >
          <Upload className="h-5 w-5" />
          {isSubmitting ? '업로드 중...' : '매뉴얼 업로드'}
        </button>
      </form>

      {isSubmitting && (
        <div className="absolute inset-0 z-20 grid place-items-center rounded-2xl bg-slate-950/85 backdrop-blur-sm">
          <div className="w-full max-w-[440px] px-8 text-center">
            <div className="mx-auto grid h-20 w-20 place-items-center rounded-full border border-blue-400/40 bg-blue-500/10 shadow-[0_0_42px_rgba(37,99,235,0.38)]">
              <Loader2 className="h-10 w-10 animate-spin text-blue-300" />
            </div>

            <p className="mt-6 text-[15px] font-black tracking-[0.24em] text-blue-300">UPLOADING & INDEXING</p>
            <h3 className="mt-3 text-[26px] font-black tracking-[-0.05em] text-white">매뉴얼 업로드 중</h3>
            <p className="mt-2 text-[14px] font-semibold text-slate-400">
              PDF 청킹 → 임베딩 → 벡터 DB 색인까지 자동 수행합니다.
              <br />
              대용량 매뉴얼은 1~2분 이상 걸릴 수 있습니다.
            </p>

            <div className="mt-7 grid grid-cols-4 gap-2">
              {STAGE_LABELS.map((label, index) => {
                const isDone = index < stageIndex;
                const isActive = index === stageIndex;
                return (
                  <div key={label} className="flex flex-col items-center gap-2">
                    <span
                      className={`grid h-9 w-9 place-items-center rounded-full border text-xs font-black transition ${
                        isDone
                          ? 'border-blue-400 bg-blue-600 text-white shadow-[0_0_16px_rgba(37,99,235,0.45)]'
                          : isActive
                            ? 'border-blue-300 bg-slate-950 text-blue-200 shadow-[0_0_16px_rgba(59,130,246,0.32)]'
                            : 'border-slate-600 bg-slate-950 text-slate-500'
                      }`}
                    >
                      {isDone ? <CheckCircle2 className="h-4 w-4" /> : index + 1}
                    </span>
                    <span className={`text-[11px] font-bold ${isActive || isDone ? 'text-slate-200' : 'text-slate-500'}`}>
                      {label}
                    </span>
                  </div>
                );
              })}
            </div>

            <div className="mt-6 inline-flex items-center gap-2 rounded-full border border-slate-700 bg-slate-900/60 px-4 py-2 text-[13px] font-bold text-slate-300">
              경과 시간: <span className="font-mono text-blue-300">{elapsedSec}s</span>
            </div>

            {values.file && (
              <p className="mt-4 truncate text-[12px] font-medium text-slate-500">{values.file.name}</p>
            )}
          </div>
        </div>
      )}
    </Panel>
  );
}
