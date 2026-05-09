import { BookOpen, Clock3, Search, ShieldCheck } from 'lucide-react';

export const searchGuideCards = [
  {
    title: '오류코드 검색',
    description: 'OPE03, F081, ALM197 등 매뉴얼에 등재된 오류코드를 직접 입력해 검색합니다.',
    icon: Search,
  },
  {
    title: '설비명 검색',
    description: '모터, 컨베이어, 프레스 등 설비명으로 문제 원인을 탐색합니다.',
    icon: ShieldCheck,
  },
  {
    title: '매뉴얼 매칭',
    description: '등록된 PDF 매뉴얼에서 해당 코드 페이지를 자동으로 찾아 인용합니다.',
    icon: BookOpen,
  },
  {
    title: '최근 이력',
    description: '작업자가 최근 검색한 오류 이력을 빠르게 다시 확인합니다.',
    icon: Clock3,
  },
] as const;
