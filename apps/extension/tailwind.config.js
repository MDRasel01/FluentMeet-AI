/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: [
    './sidepanel.html',
    './src/**/*.{js,ts,jsx,tsx}',
    './ExtensionApp.tsx',
    '../../design-system/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          primary: '#2563EB',
          secondary: '#4F46E5',
        }
      }
    },
  },
  plugins: [],
};

