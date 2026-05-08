import { AlertTriangle, BookOpen, ChevronRight } from 'lucide-react';

export const adminTabs = ['매뉴얼 등록', '오류코드 매핑', '프롬프트 관리', '사용자 승인'] as const;
export type AdminTab = (typeof adminTabs)[number];

export const manualSettings = {
  manualName: 'Valve Manual',
  category: '밸브',
  version: 'v1.0',
  errorCode: 'E-204',
};

export const errorCodeMappings = [
  { code: 'E-204', manual: 'Valve Manual', icon: ChevronRight },
  { code: 'M-102', manual: 'Motor Manual', icon: ChevronRight },
  { code: 'S-101', manual: 'Sensor Manual', icon: ChevronRight },
] as const;

export const adminStats = [
  {
    value: '5',
    unit: '종',
    label: '등록 매뉴얼',
    icon: BookOpen,
    color: 'green',
  },
  {
    value: '20',
    unit: '개',
    label: '오류코드',
    icon: AlertTriangle,
    color: 'red',
  },
] as const;
