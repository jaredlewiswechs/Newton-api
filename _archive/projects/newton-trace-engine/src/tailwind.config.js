/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./components/**/*.{js,ts,jsx,tsx}",
    "./**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Newton Color System
        newton: {
          purple: '#6D28D9',
          emerald: '#00C853',
          amber: '#FFD600',
          red: '#FF1744',
          blue: '#2979FF',
          silver: '#B0BEC5',
        },
        // f/g Ratio Colors
        fg: {
          green: '#00C853',
          yellow: '#FFD600',
          red: '#FF1744',
          verified: '#2979FF',
          historical: '#B0BEC5',
        },
      },
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
        mono: ['JetBrains Mono', 'SF Mono', 'Monaco', 'Inconsolata', 'monospace'],
      },
      animation: {
        'fade-in': 'fade-in 0.5s ease-out forwards',
        'slide-in': 'slide-in 0.5s ease-out forwards',
        'zoom-in': 'zoom-in 0.5s ease-out forwards',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      keyframes: {
        'fade-in': {
          from: { opacity: 0 },
          to: { opacity: 1 },
        },
        'slide-in': {
          from: { transform: 'translateX(-16px)', opacity: 0 },
          to: { transform: 'translateX(0)', opacity: 1 },
        },
        'zoom-in': {
          from: { transform: 'scale(0.95)', opacity: 0 },
          to: { transform: 'scale(1)', opacity: 1 },
        },
      },
      backdropBlur: {
        xs: '2px',
      },
    },
  },
  plugins: [],
}
