import { AlertTriangle, Bell, BookOpen, Clock3, Cpu, GitFork, LineChart } from 'lucide-react';

export const stats = [
  {
    label: '금일 오류 발생',
    value: '7',
    unit: '건',
    caption: '어제 대비',
    accent: '+2',
    color: 'red',
    icon: AlertTriangle,
  },
  {
    label: '이상감지 정보',
    value: '3',
    unit: '건',
    caption: '미처리',
    accent: '2건',
    color: 'amber',
    icon: Bell,
  },
  {
    label: '평균 대응 시간',
    value: '4.2',
    unit: '분',
    caption: '목표',
    accent: '5분 이내',
    color: 'green',
    icon: Clock3,
  },
  {
    label: '등록 매뉴얼',
    value: '5',
    unit: '종',
    caption: '오류코드',
    accent: '20개',
    color: 'blue',
    icon: BookOpen,
  },
] as const;

export const anomalyItems = [
  { title: '라인A 모터 이상 감지', level: '긴급', meta: 'vibration: 7.2', time: '5분전', icon: LineChart, color: 'red' },
  { title: '라인B Valve 이상 감지', level: '경고', meta: 'vibration: 7.2', time: '12분전', icon: GitFork, color: 'amber' },
  { title: '라인C 모터 이상 감지', level: '주의', meta: 'vibration: 7.2', time: '21분전', icon: Cpu, color: 'slate' },
  { title: '라인A Valve 이상 감지', level: '경고', meta: 'vibration: 7.2', time: '1시간 전', icon: GitFork, color: 'amber' },
] as const;

// UI 확인용 24시간 더미 데이터입니다. 추후 API 응답 형태에 맞춰 이 배열만 교체하면 됩니다.
export const hourlyTrendData = [
  { hour: '00', count: 1 },
  { hour: '02', count: 2 },
  { hour: '04', count: 1 },
  { hour: '06', count: 3 },
  { hour: '08', count: 6 },
  { hour: '10', count: 4 },
  { hour: '12', count: 7 },
  { hour: '14', count: 5 },
  { hour: '16', count: 8 },
  { hour: '18', count: 6 },
  { hour: '20', count: 3 },
  { hour: '22', count: 5 },
] as const;
