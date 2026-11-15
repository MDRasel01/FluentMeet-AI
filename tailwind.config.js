import plugin from 'tailwindcss/plugin';

/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}',
    './design-system/**/*.{js,ts,jsx,tsx}',
    './apps/*.{js,ts,jsx,tsx}',
    './apps/*/*.{js,ts,jsx,tsx}',
    './apps/*/src/**/*.{js,ts,jsx,tsx}',
    '!./apps/**/node_modules/**',
  ],
  theme: {
    extend: {
      screens: {
        xs: '400px',
        'smallMobile': '320px',
        'mobile': '375px',
        'largeMobile': '430px',
        'tablet': '768px',
        'smallDesktop': '1024px',
        'desktop': '1280px',
        'largeDesktop': '1440px',
        'wideDesktop': '1600px',
        '3xl': '1920px',
      },
      minHeight: { dvh: '100dvh', svh: '100svh' },
      height: { dvh: '100dvh', svh: '100svh' },
      maxHeight: { sheet: '85dvh' },
      minWidth: { touch: '44px' },
      spacing: { touch: '44px' },
      keyframes: {
        marquee: {
          from: { transform: 'translateX(0)' },
          to: { transform: 'translateX(-50%)' },
        },
        'sheet-up': {
          from: { transform: 'translateY(100%)' },
          to: { transform: 'translateY(0)' },
        },
        'fade-in': { from: { opacity: 0 }, to: { opacity: 1 } },
      },
      animation: {
        marquee: 'marquee 30s linear infinite',
        'sheet-up': 'sheet-up 280ms cubic-bezier(.32,.72,0,1)',
        'fade-in': 'fade-in 200ms ease-out',
      },
      colors: {
        primary: {
          50: '#EEF2FF',
          100: '#E0E7FF',
          200: '#C7D2FE',
          300: '#A5B4FC',
          400: '#818CF8',
          500: '#6366F1',
          600: '#4F46E5',
          700: '#4338CA',
          800: '#3730A3',
          900: '#312E81',
          950: '#1E1B4B',
          DEFAULT: '#6366F1',
        },
        neutral: {
          0: '#FFFFFF',
          50: '#F8FAFC',
          100: '#F1F5F9',
          200: '#E2E8F0',
          300: '#CBD5E1',
          400: '#94A3B8',
          500: '#64748B',
          600: '#475569',
          700: '#334155',
          800: '#1E293B',
          900: '#0F172A',
          950: '#020617',
        },
        status: {
          success: '#16A34A',
          warning: '#D97706',
          danger: '#DC2626',
          info: '#2563EB',
        },
        dark: {
          bg: '#0B1020',
          surface: '#111827',
          elevated: '#1F2937',
          subtle: '#172033',
          border: '#334155',
          borderSubtle: '#273449',
          heading: '#F8FAFC',
          body: '#CBD5E1',
          muted: '#94A3B8',
        },
      },
      fontFamily: {
        sans: ['Inter', 'Geist Sans', '-apple-system', 'sans-serif'],
        mono: ['Geist Mono', 'JetBrains Mono', 'monospace'],
      },
    },
  },
  plugins: [
    plugin(({ addUtilities }) => {
      addUtilities({
        '.pt-safe': { paddingTop: 'env(safe-area-inset-top)' },
        '.pb-safe': { paddingBottom: 'env(safe-area-inset-bottom)' },
        '.pl-safe': { paddingLeft: 'env(safe-area-inset-left)' },
        '.pr-safe': { paddingRight: 'env(safe-area-inset-right)' },
        '.pb-safe-4': { paddingBottom: 'max(1rem, env(safe-area-inset-bottom))' },
        '.pt-safe-4': { paddingTop: 'max(1rem, env(safe-area-inset-top))' },
      });
    }),
  ],
};

