export type SearchHistoryStatus = 'COMPLETED' | 'INVALID_CODE' | 'AI_ERROR';

export type SearchHistoryItem = {
  id: number;
  createdAt: string;
  keyword: string;
  result: string;
  status: SearchHistoryStatus;
};

export const searchHistoryTabs = ['검색 이력', '조치 이력', '저장 문서'] as const;

export const searchHistoryItems: SearchHistoryItem[] = [
  {
    id: 1,
    createdAt: '2026-05-08 15:24',
    keyword: 'E-204',
    result: 'AI 분석 및 매뉴얼 제공',
    status: 'COMPLETED',
  },
  {
    id: 2,
    createdAt: '2026-05-08 14:52',
    keyword: 'M-102',
    result: '모터 진동 원인 분석',
    status: 'COMPLETED',
  },
  {
    id: 3,
    createdAt: '2026-05-08 13:18',
    keyword: 'S-101',
    result: '등록되지 않은 오류 코드',
    status: 'INVALID_CODE',
  },
  {
    id: 4,
    createdAt: '2026-05-08 11:07',
    keyword: '밸브 온도 상승',
    result: '관련 매뉴얼 조회',
    status: 'COMPLETED',
  },
  {
    id: 5,
    createdAt: '2026-05-08 09:43',
    keyword: 'V-318',
    result: 'AI 서버 응답 지연',
    status: 'AI_ERROR',
  },
];
