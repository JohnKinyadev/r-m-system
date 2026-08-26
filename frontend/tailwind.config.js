/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js,ts}'],
  theme: {
    extend: {
      colors: {
        farm: {
          50:  '#f0f7f1',
          100: '#d8eedd',
          200: '#b4dcbd',
          300: '#82c294',
          400: '#52a468',
          500: '#2d8a49',
          600: '#1f6f39',
          700: '#1a5c2a',  // primary dark green
          800: '#174d25',
          900: '#133f1f',
        },
        harvest: {
          400: '#f0a500',
          500: '#e09400',  // accent amber/orange
          600: '#c47f00',
        },
      },
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui'],
      },
    },
  },
  plugins: [],
}
