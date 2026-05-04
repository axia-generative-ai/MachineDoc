import { AlertTriangle, Search, ShieldCheck, Wrench } from 'lucide-react';

export const virtualLogLines = [
  { line: 1, content: [{ text: '{', color: 'text-slate-100' }] },
  {
    line: 2,
    content: [
      { text: '"timestamp"', color: 'text-sky-400' },
      { text: ': ', color: 'text-slate-300' },
      { text: '"2025-05-10T10:15Z"', color: 'text-orange-400' },
      { text: ',', color: 'text-slate-300' },
    ],
  },
  {
    line: 3,
    content: [
      { text: '"line"', color: 'text-sky-400' },
      { text: ': ', color: 'text-slate-300' },
      { text: '"라인A"', color: 'text-orange-400' },
      { text: ',', color: 'text-slate-300' },
    ],
  },
  {
    line: 4,
    content: [
      { text: '"equipment"', color: 'text-sky-400' },
      { text: ': ', color: 'text-slate-300' },
      { text: '"M-102"', color: 'text-orange-400' },
      { text: ',', color: 'text-slate-300' },
    ],
  },
  {
    line: 5,
    content: [
      { text: '"vibraton"', color: 'text-sky-400' },
      { text: ': ', color: 'text-slate-300' },
      { text: '7.2', color: 'text-lime-400' },
      { text: ',', color: 'text-slate-300' },
    ],
  },
  {
    line: 6,
    content: [
      { text: '"temperature"', color: 'text-sky-400' },
      { text: ': ', color: 'text-slate-300' },
      { text: '68.5', color: 'text-lime-400' },
      { text: ',', color: 'text-slate-300' },
    ],
  },
  {
    line: 7,
    content: [
      { text: '"status"', color: 'text-sky-400' },
      { text: ': ', color: 'text-slate-300' },
      { text: '"warning"', color: 'text-orange-400' },
    ],
  },
  { line: 8, content: [{ text: '}', color: 'text-slate-100' }] },
] as const;

export const analysisResults = [
  {
    label: '이상 여부',
    value: '이상',
    icon: AlertTriangle,
    color: 'red',
  },
  {
    label: '추정 원인',
    value: '모터 진동 증가',
    icon: Search,
    color: 'blue',
  },
  {
    label: '권장 조치',
    value: '베어링 점검, 윤활 확인',
    icon: Wrench,
    color: 'amber',
  },
  {
    label: '신뢰도',
    value: '86%',
    icon: ShieldCheck,
    color: 'green',
  },
] as const;
