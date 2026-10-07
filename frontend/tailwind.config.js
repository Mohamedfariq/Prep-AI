/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
      },
      colors: {
        ink: '#0f1b2d',
        muted: '#8090aa',
        brand: '#5244e9',
        brandDark: '#3f32d4',
        soft: '#f4f7fb',
        line: '#dfe7f3',
      },
      boxShadow: {
        card: '0 14px 35px rgba(15, 27, 45, 0.08)',
        subtle: '0 6px 20px rgba(15, 27, 45, 0.08)',
      },
    },
  },
  plugins: [],
};
