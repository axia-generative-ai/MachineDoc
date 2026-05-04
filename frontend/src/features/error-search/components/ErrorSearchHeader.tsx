import { ChevronRight, Home } from 'lucide-react';
import { useSearchParams } from 'react-router-dom';

export function ErrorSearchHeader() {
  const [searchParams] = useSearchParams();
  const keyword = searchParams.get('q') || 'E-204';

  return (
    <div className="mb-6">
      <div className="mb-4 flex items-center gap-3 text-[16px] font-semibold text-slate-400">
        <Home className="h-5 w-5 text-slate-300" />
        <span className="flex items-center gap-3">
          <ChevronRight className="h-4 w-4 text-slate-500" />
          오류 검색
        </span>
        <span className="flex items-center gap-3">
          <ChevronRight className="h-4 w-4 text-slate-500" />
          {keyword} 결과
        </span>
      </div>
      <div className="flex items-end gap-5">
        <h1 className="text-[40px] font-black tracking-[-0.06em] text-white">{keyword} 검색 결과</h1>
        <span className="pb-2 text-[20px] font-semibold text-slate-400">- 관련 매뉴얼 3건</span>
      </div>
    </div>
  );
}
