import { History } from 'lucide-react';

export function SearchHistoryHeader() {
  return (
    <header className="mb-6 flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
      <div>
        <p className="mb-2 flex items-center gap-2 text-[15px] font-black tracking-[0.2em] text-blue-300">
          <History className="h-5 w-5" />
          SEARCH HISTORY
        </p>
        <h1 className="text-[40px] font-black tracking-[-0.07em] text-white">검색 이력</h1>
        <p className="mt-2 text-[17px] font-semibold tracking-[-0.04em] text-slate-400">
          작업자가 검색한 오류 코드와 분석 결과 상태를 확인합니다.
        </p>
      </div>
    </header>
  );
}
