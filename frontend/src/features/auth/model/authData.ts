export const authScenarios = {
  login: {
    title: '로그인',
    eyebrow: 'FACTORYGUARD',
    description: '설비 이상 대응을 더 빠르게',
    submitLabel: '로그인',
    secondaryLabel: '회원가입',
    secondaryTo: '/signup',
  },
  signup: {
    title: '회원가입',
    eyebrow: 'FACTORYGUARD',
    description: '승인 요청에 필요한 기본 정보를 입력해주세요',
    submitLabel: '회원가입',
    secondaryLabel: '로그인',
    secondaryTo: '/login',
  },
} as const;
