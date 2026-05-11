import { useEffect, useState } from 'react';
import { CheckCircle2, RefreshCw, Save, Sparkles } from 'lucide-react';

import { Panel } from '../../../shared/ui/Panel';
import { ApiError } from '../../../shared/api/apiError';
import { promptApi, type PromptItem } from '../infra/prompt.api';

const DEFAULT_KEY = 'rag_korean_skeleton';

function formatTimestamp(iso: string | null): string {
  if (!iso) return '-';
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return iso;
  return date.toLocaleString('ko-KR', { hour12: false });
}

export function AdminPromptPanel() {
  const [prompts, setPrompts] = useState<PromptItem[]>([]);
  const [activeKey, setActiveKey] = useState<string>(DEFAULT_KEY);
  const [draft, setDraft] = useState<string>('');
  const [description, setDescription] = useState<string>('');
  const [updatedAt, setUpdatedAt] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const load = async () => {
    setIsLoading(true);
    setErrorMessage(null);
    try {
      let list = await promptApi.list();
      if (list.length === 0) {
        // ai-service가 첫 query에서 자동 시드하므로, 한 번 query를 트리거 후 다시 fetch
        try {
          await promptApi.get(DEFAULT_KEY).catch(() => null);
        } catch {
          /* ignore — 서버가 시드 못해도 빈 상태 표시 */
        }
        list = await promptApi.list();
      }
      setPrompts(list);
      const target = list.find((p) => p.key === activeKey) ?? list[0];
      if (target) {
        setActiveKey(target.key);
        setDraft(target.content);
        setDescription(target.description ?? '');
        setUpdatedAt(target.updatedAt);
      }
    } catch (error) {
      if (error instanceof ApiError && error.status === 403) {
        setErrorMessage('관리자 권한이 필요합니다.');
      } else {
        setErrorMessage(error instanceof Error ? error.message : '프롬프트를 불러오지 못했습니다.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    void load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const switchKey = (key: string) => {
    const target = prompts.find((p) => p.key === key);
    if (!target) return;
    setActiveKey(key);
    setDraft(target.content);
    setDescription(target.description ?? '');
    setUpdatedAt(target.updatedAt);
    setSuccessMessage(null);
    setErrorMessage(null);
  };

  const handleSave = async () => {
    setIsSaving(true);
    setErrorMessage(null);
    setSuccessMessage(null);
    try {
      const updated = await promptApi.upsert(activeKey, {
        content: draft,
        description: description.trim() || undefined,
      });
      setUpdatedAt(updated.updatedAt);
      setSuccessMessage('저장 완료. 다음 검색부터 새 프롬프트가 적용됩니다 (캐시 30초).');
      setPrompts((prev) => prev.map((p) => (p.key === updated.key ? updated : p)));
    } catch (error) {
      if (error instanceof ApiError) {
        if (error.status === 401) setErrorMessage('로그인 정보가 만료되었습니다.');
        else if (error.status === 403) setErrorMessage('관리자 권한이 필요합니다.');
        else setErrorMessage(error.message || '저장 중 오류가 발생했습니다.');
      } else {
        setErrorMessage('저장 중 오류가 발생했습니다.');
      }
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <Panel className="p-6">
      <div className="flex items-start justify-between border-b border-slate-700/80 pb-5">
        <div>
          <h2 className="flex items-center gap-3 text-[24px] font-black tracking-[-0.05em] text-white">
            <Sparkles className="h-6 w-6 text-blue-400" />
            프롬프트 관리
          </h2>
          <p className="mt-2 text-[13px] font-semibold text-slate-500">
            ai-service가 LLM 호출 시 사용하는 프롬프트 스켈레톤입니다. 저장 시 즉시 DB에 반영되며 다음 검색부터 적용됩니다.
            (ai-service 캐시 TTL 30초)
          </p>
        </div>
        <button
          type="button"
          onClick={() => void load()}
          disabled={isLoading}
          className="grid h-10 w-10 place-items-center rounded-lg border border-slate-700 text-slate-300 transition hover:border-blue-400/60 hover:text-blue-300 disabled:opacity-50"
          aria-label="새로고침"
        >
          <RefreshCw className={`h-5 w-5 ${isLoading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {prompts.length > 1 && (
        <div className="mt-5 flex flex-wrap gap-2">
          {prompts.map((p) => (
            <button
              key={p.key}
              type="button"
              onClick={() => switchKey(p.key)}
              className={`h-9 rounded-lg border px-3 text-[13px] font-black transition ${
                p.key === activeKey
                  ? 'border-blue-400 bg-blue-500/15 text-blue-200'
                  : 'border-slate-700 bg-slate-950/30 text-slate-400 hover:border-blue-400/50'
              }`}
            >
              {p.key}
            </button>
          ))}
        </div>
      )}

      {errorMessage && (
        <p className="mt-4 rounded-lg border border-red-500/40 bg-red-500/10 px-4 py-3 text-[14px] font-bold text-red-300">
          {errorMessage}
        </p>
      )}

      {isLoading ? (
        <p className="mt-10 text-center text-[14px] font-bold text-slate-400">불러오는 중...</p>
      ) : (
        <div className="mt-5 space-y-4">
          <div className="flex items-center justify-between text-[13px] font-bold text-slate-400">
            <span>
              <span className="font-mono text-blue-300">{activeKey}</span>
              <span className="ml-3 text-slate-500">최근 수정: {formatTimestamp(updatedAt)}</span>
            </span>
          </div>

          <label className="block">
            <span className="mb-2 block text-[14px] font-semibold text-slate-400">설명 (선택)</span>
            <input
              value={description}
              onChange={(event) => setDescription(event.target.value)}
              placeholder="이 프롬프트의 용도를 간단히 적어두면 다른 관리자가 알기 쉬워집니다."
              className="h-11 w-full rounded-lg border border-slate-700 bg-slate-950/30 px-4 text-[14px] font-semibold text-white outline-none focus:border-blue-400/70"
            />
          </label>

          <label className="block">
            <span className="mb-2 block text-[14px] font-semibold text-slate-400">프롬프트 본문</span>
            <textarea
              value={draft}
              onChange={(event) => setDraft(event.target.value)}
              rows={20}
              spellCheck={false}
              className="block w-full resize-y rounded-lg border border-slate-700 bg-slate-950/40 p-4 font-mono text-[13px] leading-relaxed text-slate-100 outline-none focus:border-blue-400/70"
            />
          </label>

          {successMessage && (
            <p className="flex items-center gap-2 rounded-lg border border-emerald-500/40 bg-emerald-500/10 px-4 py-3 text-[13px] font-bold text-emerald-300">
              <CheckCircle2 className="h-4 w-4" />
              {successMessage}
            </p>
          )}

          <button
            type="button"
            onClick={() => void handleSave()}
            disabled={isSaving || draft.trim() === ''}
            className="inline-flex h-11 items-center gap-2 rounded-lg bg-blue-600 px-5 text-[14px] font-black text-white shadow-[0_0_20px_rgba(37,99,235,0.35)] transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:bg-slate-700 disabled:text-slate-400 disabled:shadow-none"
          >
            <Save className="h-4 w-4" />
            {isSaving ? '저장 중...' : '저장'}
          </button>
        </div>
      )}
    </Panel>
  );
}
