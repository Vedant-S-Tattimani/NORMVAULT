/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        parchment: {
          base: '#F6F2EA',
          surface: '#FCFAF6',
          subtle: '#EFE8DC',
          border: '#D9D0C1',
          divider: '#E4DDD0',
        },
        ink: {
          text: '#1E2320',
          muted: '#686358',
          faint: '#9E988C',
          dark: '#111412',
        },
        mineral: {
          blue: '#2C6E80',
          dark: '#1A4A58',
          light: '#E8F1F4',
        },
        brand: {
          navy: '#0A2254',
          navyDark: '#07183D',
          blue: '#2563EB',
          blueLight: '#EFF6FF',
        },
        status: {
          sage: '#2D5A43',
          sageBg: '#EBF2EE',
          sageBorder: '#C4D9CD',
          amber: '#8A5818',
          amberBg: '#FDF5E6',
          amberBorder: '#EBD2A6',
          crimson: '#8C2525',
          crimsonBg: '#FBF0F0',
          crimsonBorder: '#E8C0C0',
          indigo: '#1E3A5F',
          indigoBg: '#EEF3F8',
          indigoBorder: '#C6D8E8',
        },
      },
      fontFamily: {
        serif: ['"Cormorant Garamond"', '"EB Garamond"', 'Georgia', 'serif'],
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
      },
      boxShadow: {
        'parchment': '0 4px 20px -2px rgba(100, 80, 50, 0.05), 0 2px 6px -1px rgba(100, 80, 50, 0.03)',
        'parchment-lg': '0 10px 30px -4px rgba(100, 80, 50, 0.08), 0 4px 12px -2px rgba(100, 80, 50, 0.04)',
      },
    },
  },
  plugins: [],
}
