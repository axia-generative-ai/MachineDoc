import { useEffect, useState } from 'react';
import { CheckCircle2, X } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

import { ApiError } from '../../../../shared/api/apiError';
import {
  ACTION_STATUS_OPTIONS,
  actionLogApi,
  type ActionStatusValue,
} from '../../../search-history/infra/actionLog.api';

type Props = {
  historyId: number;
  query: string;
  open: boolean;
  onClose: () => void;
};

export function ActionLogModal({ historyId, query, open, onClose }: Props) {
  const navigate = useNavigate();
  const [status, setStatus] = useState<ActionStatusValue>('완료');
  const [comment, setComment] = useState('');
  const [duration, setDuration] = useState<string>('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  useEffect(() => {
    if (!open) {
      setErrorMessage(null);
      setSuccessMessage(null);
    }
  }, [open]);

  if (!open) return null;

  const handleSubmit = async () => {
    setErrorMessage(null);
    setSuccessMessage(null);
    const durationNum = duration.trim() === '' ? undefined : Number(duration);
    if (durationNum !== undefined && (Number.isNaN(durationNum) || durationNum < 0)) {
      setErrorMessage('?뚯슂 ?쒓컙? 0 ?댁긽???レ옄?ъ빞 ?⑸땲??');
      return;
    }
    setIsSubmitting(true);
    try {
      await actionLogApi.upsert(historyId, {
        actionStatus: status,
        comment: comment.trim() || undefined,
        duration: durationNum,
      });
      setSuccessMessage('議곗튂 寃곌낵媛 ??λ릺?덉뒿?덈떎. ??쒕낫?쒕줈 ?대룞?⑸땲??');
      // ?ъ슜?먭? success 硫붿떆吏瑜??좉퉸 蹂????덈룄濡?吏㏃? delay ??dashboard ?대룞.
      setTimeout(() => {
        onClose();
        navigate('/dashboard');
      }, 800);
    } catch (error) {
      if (error instanceof ApiError) {
        if (error.status === 401) setErrorMessage('濡쒓렇???뺣낫媛 留뚮즺?섏뿀?듬땲??');
        else if (error.status === 403) setErrorMessage('蹂몄씤 寃???대젰?먮쭔 議곗튂瑜??낅젰?????덉뒿?덈떎.');
        else if (error.status === 404) setErrorMessage('?대떦 寃???대젰??李얠쓣 ???놁뒿?덈떎.');
        else setErrorMessage(error.message || '???以??ㅻ쪟媛 諛쒖깮?덉뒿?덈떎.');
      } else {
        setErrorMessage('???以??ㅻ쪟媛 諛쒖깮?덉뒿?덈떎.');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 grid place-items-center bg-black/70 backdrop-blur-sm" onClick={onClose}>
      <div
        className="w-full max-w-[520px] rounded-2xl border border-slate-700/80 bg-slate-950/95 p-6 shadow-[0_24px_80px_rgba(0,0,0,0.6)]"
        onClick={(event) => event.stopPropagation()}
      >
        <div className="flex items-start justify-between">
          <div>
            <p className="text-[12px] font-black tracking-[0.24em] text-blue-300">ACTION REPORT</p>
            <h2 className="mt-2 text-[22px] font-black tracking-[-0.05em] text-white">議곗튂 寃곌낵 ?낅젰</h2>
            <p className="mt-1 text-[13px] font-semibold text-slate-400">
              寃??肄붾뱶 <span className="font-mono text-blue-300">{query}</span> 쨌 history_id={historyId}
            </p>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="grid h-9 w-9 place-items-center rounded-lg border border-slate-700 text-slate-400 transition hover:border-red-400/70 hover:text-red-300"
            aria-label="?リ린"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        <form
          className="mt-6 space-y-4"
          onSubmit={(event) => {
            event.preventDefault();
            void handleSubmit();
          }}
        >
          <label className="block">
            <span className="mb-2 block text-[14px] font-semibold text-slate-400">議곗튂 ?곹깭</span>
            <div className="grid grid-cols-2 gap-2">
              {ACTION_STATUS_OPTIONS.map((option) => (
                <label
                  key={option}
                  className={`flex h-11 cursor-pointer items-center justify-center gap-2 rounded-lg border text-[14px] font-bold transition ${
                    status === option
                      ? 'border-blue-400 bg-blue-500/15 text-blue-200'
                      : 'border-slate-700 bg-slate-950/30 text-slate-400 hover:border-blue-400/50 hover:text-blue-300'
                  }`}
                >
                  <input
                    type="radio"
                    name="action_status"
                    value={option}
                    checked={status === option}
                    onChange={() => setStatus(option)}
                    className="h-4 w-4 accent-blue-600"
                  />
                  {option}
                </label>
              ))}
            </div>
          </label>

          <label className="block">
            <span className="mb-2 block text-[14px] font-semibold text-slate-400">肄붾찘??(?좏깮)</span>
            <textarea
              value={comment}
              onChange={(event) => setComment(event.target.value)}
              rows={3}
              placeholder="議곗튂 ?댁슜쨌愿李??ы빆쨌異붽? ?먭? ?꾩슂 ??ぉ ?깆쓣 ?먯쑀濡?쾶 ?낅젰?섏꽭??"
              className="w-full rounded-lg border border-slate-700 bg-slate-950/30 p-3 text-[14px] font-semibold text-white outline-none focus:border-blue-400/70"
            />
          </label>

          <label className="block">
            <span className="mb-2 block text-[14px] font-semibold text-slate-400">?뚯슂 ?쒓컙 (遺? ?좏깮)</span>
            <input
              value={duration}
              onChange={(event) => setDuration(event.target.value)}
              type="number"
              min={0}
              placeholder="?? 15"
              className="h-11 w-full rounded-lg border border-slate-700 bg-slate-950/30 px-4 text-[15px] font-semibold text-white outline-none focus:border-blue-400/70"
            />
          </label>

          {errorMessage && (
            <p className="rounded-lg border border-red-500/40 bg-red-500/10 px-4 py-3 text-[13px] font-bold text-red-300">
              {errorMessage}
            </p>
          )}
          {successMessage && (
            <p className="flex items-center gap-2 rounded-lg border border-emerald-500/40 bg-emerald-500/10 px-4 py-3 text-[13px] font-bold text-emerald-300">
              <CheckCircle2 className="h-4 w-4" />
              {successMessage}
            </p>
          )}

          <div className="flex gap-3">
            <button
              type="button"
              onClick={onClose}
              className="h-11 flex-1 rounded-lg border border-slate-700 bg-slate-950/30 text-[14px] font-black text-slate-300 transition hover:border-slate-500 hover:text-slate-200"
            >
              ?リ린
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="h-11 flex-1 rounded-lg bg-blue-600 text-[14px] font-black text-white shadow-[0_0_20px_rgba(37,99,235,0.35)] transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:bg-slate-700 disabled:text-slate-400 disabled:shadow-none"
            >
              {isSubmitting ? '저장 중...' : '저장'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

