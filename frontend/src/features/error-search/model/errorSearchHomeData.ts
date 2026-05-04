import { BookOpen, Clock3, Search, ShieldCheck } from 'lucide-react';

export const quickSearchTags = ['E-204', 'M-102', 'S-101', '밸브 온도', '모터 진동', '센서 통신'] as const;

export const recentSearches = [
  { keyword: 'E-204 밸브 온도 상승', time: '5분 전' },
  { keyword: 'M-102 모터 진동 초과', time: '18분 전' },
  { keyword: 'S-101 센서 통신 지연', time: '1시간 전' },
] as const;

export const searchGuideCards = [
  {
    title: '오류코드 검색',
    description: 'E-204, M-102처럼 오류코드를 직접 입력해 관련 매뉴얼을 찾습니다.',
    icon: Search,
  },
  {
    title: '설비명 검색',
    description: '밸브, 모터, 센서 등 설비명으로 문제 원인을 탐색합니다.',
    icon: ShieldCheck,
  },
  {
    title: '매뉴얼 매칭',
    description: '등록된 PDF 매뉴얼과 오류코드를 비교해 관련 문서를 보여줍니다.',
    icon: BookOpen,
  },
  {
    title: '최근 이력',
    description: '작업자가 최근 검색한 오류 이력을 빠르게 다시 확인합니다.',
    icon: Clock3,
  },
] as const;
