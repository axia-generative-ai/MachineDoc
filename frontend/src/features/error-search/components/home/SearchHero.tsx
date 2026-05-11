import { useEffect, useState } from 'react';
import { Search } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

import { manualApi } from '../../infra/manual.api';
import { Panel } from '../../../../shared/ui/Panel';

export function SearchHero() {
  const navigate = useNavigate();
  const [keyword, setKeyword] = useState('');
  const [hasSearchError, setHasSearchError] = useState(false);
  const [quickTags, setQuickTags] = useState<string[]>([]);

  useEffect(() => {
    let cancelled = false;
    manualApi
      .listErrorCodeMappings()
      .then((data) => {
        if (cancelled) return;
        // 매핑된 코드 중 앞에서 6개 (정렬 = code_name asc)
        const codes = Array.from(new Set(data.map((m) => m.codeName))).slice(0, 6);
        setQuickTags(codes);
      })
      .catch(() => {
        if (cancelled) return;
        setQuickTags([]);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const handleSearch = () => {
    const nextKeyword = keyword.trim().toUpperCase();
    if (!nextKeyword) {
      setHasSearchError(true);
      return;
    }

    setHasSearchError(false);
    navigate(`/error-search/result?q=${encodeURIComponent(nextKeyword)}`);
  };

  const handleQuickSearch = (tag: string) => {
    navigate(`/error-search/result?q=${encodeURIComponent(tag)}`);
  };

  return (
    <Panel className="p-7">
      <div className="mx-auto max-w-[980px] text-center">
        <p className="mb-3 text-[18px] font-bold tracking-[-0.04em] text-blue-400">ERROR MANUAL SEARCH</p>
        <h1 className="text-[36px] font-black tracking-[-0.07em] text-white md:text-[44px]">오류코드 또는 설비명을 검색하세요</h1>
        <p className="mt-4 text-[17px] font-semibold tracking-[-0.04em] text-slate-400 md:text-[19px]">
          입력한 키워드를 기준으로 관련 매뉴얼, 원인, 조치 절차를 빠르게 확인합니다.
        </p>

        <div
          className={`mt-9 flex h-[72px] items-center gap-4 rounded-2xl border bg-slate-950/60 px-6 transition ${
            hasSearchError
              ? 'border-red-500 shadow-[0_0_34px_rgba(239,68,68,0.28)]'
              : 'border-blue-400/60 shadow-[0_0_34px_rgba(37,99,235,0.22)]'
          }`}
        >
          <Search className="h-8 w-8 shrink-0 text-blue-400" />
          <input
            value={keyword}
            onChange={(event) => {
              setKeyword(event.target.value);
              if (event.target.value.trim()) {
                setHasSearchError(false);
              }
            }}
            onKeyDown={(event) => {
              if (event.key === 'Enter') {
                handleSearch();
              }
            }}
            className="h-full min-w-0 flex-1 bg-transparent text-left text-[20px] font-semibold text-white outline-none placeholder:text-slate-500 md:text-[24px]"
            placeholder="예: OPE03, F081, ALM197, AL.50"
          />
          <button
            type="button"
            onClick={handleSearch}
            className="h-12 rounded-xl bg-blue-600 px-6 text-[17px] font-black text-white shadow-[0_0_24px_rgba(37,99,235,0.4)] transition hover:bg-blue-500 md:px-8 md:text-[18px]"
          >
            검색
          </button>
        </div>
        {hasSearchError && <p className="mt-3 text-left text-[15px] font-bold text-red-400">검색어를 입력해주세요.</p>}

        {quickTags.length > 0 && (
          <div className="mt-6 flex flex-wrap justify-center gap-3">
            {quickTags.map((tag) => (
              <button
                key={tag}
                type="button"
                onClick={() => handleQuickSearch(tag)}
                className="rounded-full border border-slate-700 bg-slate-950/35 px-5 py-2 font-mono text-[15px] font-bold text-slate-300 transition hover:border-blue-400/70 hover:text-blue-300"
              >
                {tag}
              </button>
            ))}
          </div>
        )}
      </div>
    </Panel>
  );
}
