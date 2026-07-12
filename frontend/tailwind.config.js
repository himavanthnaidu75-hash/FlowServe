/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        bg: { primary: '#0a0a0a', secondary: '#111111', tertiary: '#1a1a1a' },
        surface: { DEFAULT: '#141414', hover: '#1f1f1f' },
        border: { DEFAULT: '#2a2a2a', light: '#333333' },
        red: {
          900: '#1a0000', 800: '#3b0000', 700: '#6b0000', 600: '#9f0000',
          500: '#dc2626', 400: '#ef4444', 300: '#f87171', 200: '#fca5a5', 100: '#fee2e2',
        },
        green: { 900: '#052e1b', 800: '#064e3b', 700: '#047857', 600: '#059669', 500: '#10b981', 400: '#34d399', 300: '#6ee7b7', 200: '#a7f3d0', 100: '#d1fae5' },
        yellow: { 900: '#422006', 800: '#713f12', 700: '#854d0e', 600: '#a16207', 500: '#eab308', 400: '#facc15', 300: '#fde047', 200: '#fef08a', 100: '#fef9c3' },
        blue: { 900: '#0c1e3a', 800: '#172554', 700: '#1e3a8a', 600: '#1d4ed8', 500: '#3b82f6', 400: '#60a5fa', 300: '#93c5fd', 200: '#bfdbfe', 100: '#dbeafe' },
        indigo: { 900: '#1e1b4b', 800: '#312e81', 700: '#3730a3', 600: '#4338ca', 500: '#6366f1', 400: '#818cf8', 300: '#a5b4fc', 200: '#c7d2fe', 100: '#e0e7ff' },
      },
      fontFamily: {
        display: ['"Plus Jakarta Sans"', 'sans-serif'],
        sans: ['Inter', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
      },
    },
  },
  plugins: [],
}
