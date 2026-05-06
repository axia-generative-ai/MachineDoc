import { ClipboardList, Droplet, FileText, Snowflake, Stethoscope, Wrench } from 'lucide-react';

export const errorSearchBreadcrumbs = ['홈', '오류 검색', 'E-204 결과'] as const;

export const actionSteps = [
  {
    step: 1,
    title: '설비 상태 및 알람 코드 확인',
    icon: ClipboardList,
  },
  {
    step: 2,
    title: '관련 부품의 온도/압력 점검',
    icon: Stethoscope,
  },
  {
    step: 3,
    title: '밸브 내부 누설 여부 확인',
    icon: Droplet,
  },
  {
    step: 4,
    title: '필요 시 부품 교체 후 재가동',
    icon: Wrench,
  },
] as const;

export const relatedManuals = [
  {
    title: 'Valve Manual',
    type: 'PDF',
    matchRate: 95,
    icon: FileText,
  },
  {
    title: 'Valve Cooling',
    type: 'PDF',
    matchRate: 82,
    icon: Snowflake,
  },
  {
    title: 'Pressure Sensor',
    type: 'PDF',
    matchRate: 68,
    icon: Stethoscope,
  },
] as const;
