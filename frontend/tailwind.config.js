/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Pretendard', 'Noto Sans KR', 'ui-sans-serif', 'system-ui'],
      },
      boxShadow: {
        glow: '0 0 32px rgba(35, 132, 255, 0.22)',
        panel: 'inset 0 1px 0 rgba(255,255,255,0.06), 0 24px 60px rgba(0,0,0,0.35)',
      },
      backgroundImage: {
        'factory-radial': 'radial-gradient(circle at 20% 10%, rgba(35,132,255,0.16), transparent 28%), radial-gradient(circle at 88% 0%, rgba(39,210,113,0.08), transparent 24%), linear-gradient(135deg, #050b10 0%, #07111a 45%, #03070b 100%)',
      },
    },
  },
  plugins: [],
};
