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
        brand: {
          obsidian: '#09090b',
          abyss: '#030303',
          purple: {
            deep: '#1e1b4b',
            neon: '#8b5cf6',
            glow: '#a78bfa',
          },
          cyan: {
            deep: '#083344',
            neon: '#06b6d4',
            glow: '#22d3ee',
          },
          emerald: {
            deep: '#022c22',
            neon: '#10b981',
            glow: '#34d399',
          },
          amber: {
            deep: '#451a03',
            neon: '#f59e0b',
            glow: '#fbbf24',
          },
          rose: {
            deep: '#4c0519',
            neon: '#f43f5e',
            glow: '#fb7185',
          },
          slate: {
            950: '#020617',
            900: '#0f172a',
            800: '#1e293b',
            700: '#334155',
            400: '#94a3b8',
            200: '#e2e8f0',
          }
        }
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'glass-gradient': 'linear-gradient(135deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.01) 100%)',
        'glass-premium': 'linear-gradient(135deg, rgba(139, 92, 246, 0.1) 0%, rgba(6, 182, 212, 0.05) 100%)',
      },
      boxShadow: {
        'glass': '0 8px 32px 0 rgba(0, 0, 0, 0.37)',
        'glass-glow-purple': '0 0 25px 2px rgba(139, 92, 246, 0.25)',
        'glass-glow-cyan': '0 0 25px 2px rgba(6, 182, 212, 0.25)',
        'glass-glow-emerald': '0 0 25px 2px rgba(16, 185, 129, 0.25)',
      },
      backdropBlur: {
        'xs': '2px',
      }
    },
  },
  plugins: [],
}
