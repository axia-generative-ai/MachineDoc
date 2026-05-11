import { AlertTriangle, BookOpen, ChevronRight } from 'lucide-react';

export const adminTabs = ['매뉴얼 등록', '오류코드 매핑', '프롬프트 관리', '사용자 승인'] as const;
export type AdminTab = (typeof adminTabs)[number];

export const manualSettings = {
  manualName: 'YASKAWA GA700 모터 매뉴얼',
  category: '점검',
  version: 'v1.0',
  errorCode: 'OPE03',
};

export const errorCodeMappings = [
  { code: 'OPE03', manual: 'YASKAWA GA700 모터 매뉴얼', icon: ChevronRight },
  { code: 'F081', manual: 'Rockwell PowerFlex 컨베이어 매뉴얼', icon: ChevronRight },
  { code: 'ALM197', manual: 'FANUC 0M 프레스 매뉴얼', icon: ChevronRight },
  { code: '10025', manual: 'ABB IRB 로봇 매뉴얼', icon: ChevronRight },
  { code: 'AL.50', manual: 'Mitsubishi Servo 용접기 매뉴얼', icon: ChevronRight },
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
