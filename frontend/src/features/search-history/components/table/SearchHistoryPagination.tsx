import { ChevronLeft, ChevronRight } from 'lucide-react';

type SearchHistoryPaginationProps = {
  currentPage: number;
  pageSize: number;
  totalItems: number;
  onPageChange: (page: number) => void;
};

function getVisiblePages(currentPage: number, totalPages: number) {
  const start = Math.max(1, Math.min(currentPage - 1, totalPages - 2));
  const end = Math.min(totalPages, start + 2);

  return Array.from({ length: end - start + 1 }, (_, index) => start + index);
}

export function SearchHistoryPagination({ currentPage, pageSize, totalItems, onPageChange }: SearchHistoryPaginationProps) {
  const totalPages = Math.max(1, Math.ceil(totalItems / pageSize));

  if (totalPages <= 1) return null;

  const visiblePages = getVisiblePages(currentPage, totalPages);

  return (
    <div className="mt-5 flex items-center justify-center gap-2 text-[14px] font-black text-slate-500">
      <button
        type="button"
        onClick={() => onPageChange(Math.max(1, currentPage - 1))}
        disabled={currentPage === 1}
        className="grid h-8 w-8 place-items-center rounded-lg transition hover:bg-slate-800 hover:text-blue-300 disabled:cursor-not-allowed disabled:opacity-40"
        aria-label="이전 페이지"
      >
        <ChevronLeft className="h-4 w-4" />
      </button>
      {visiblePages.map((page) => (
        <button
          key={page}
          type="button"
          onClick={() => onPageChange(page)}
          className={`grid h-8 w-8 place-items-center rounded-lg transition ${
            page === currentPage ? 'bg-blue-600 text-white shadow-[0_0_18px_rgba(37,99,235,0.34)]' : 'hover:bg-slate-800 hover:text-blue-300'
          }`}
        >
          {page}
        </button>
      ))}
      <button
        type="button"
        onClick={() => onPageChange(Math.min(totalPages, currentPage + 1))}
        disabled={currentPage === totalPages}
        className="grid h-8 w-8 place-items-center rounded-lg transition hover:bg-slate-800 hover:text-blue-300 disabled:cursor-not-allowed disabled:opacity-40"
        aria-label="다음 페이지"
      >
        <ChevronRight className="h-4 w-4" />
      </button>
    </div>
  );
}
