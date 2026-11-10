/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        terminal: {
          bg: "#080c14",
          surface: "#0f172a",
          card: "#131d31",
          border: "#1e293b",
          highlight: "#1e3a8a",
        },
        market: {
          green: "#10b981",
          red: "#ef4444",
          cyan: "#06b6d4",
          blue: "#3b82f6",
          purple: "#8b5cf6",
          amber: "#f59e0b"
        }
      },
      fontFamily: {
        mono: ['JetBrains Mono', 'Menlo', 'Consolas', 'monospace'],
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
