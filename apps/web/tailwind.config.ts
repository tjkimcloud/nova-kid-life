import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      // ── Brand Colors ──────────────────────────────────────────────────────
      // Values mirror CSS custom properties in globals.css.
      // Hardcoded here so Tailwind opacity modifiers (bg-primary-500/50) work.
      colors: {
        primary: {
          50:  '#FFFBEB',
          100: '#FEF3C7',
          200: '#FDE68A',
          300: '#FCD34D',
          400: '#FBBF24',
          500: '#F59E0B',
          600: '#D97706',
          700: '#B45309',
          800: '#92400E',
          900: '#78350F',
          950: '#451A03',
        },
        secondary: {
          50:  '#F4F7F4',
          100: '#E2EAE2',
          200: '#C5D5C6',
          300: '#9DB89E',
          400: '#739775',
          500: '#537A55',
          600: '#406143',
          700: '#344E37',
          800: '#2B3F2D',
          900: '#243427',
          950: '#131D15',
        },
      },
      // ── Typography ────────────────────────────────────────────────────────
      fontFamily: {
        heading: ['var(--font-nunito)', 'Nunito', 'ui-rounded', 'sans-serif'],
        body:    ['var(--font-plus-jakarta)', 'Plus Jakarta Sans', 'ui-sans-serif', 'sans-serif'],
      },
      // ── Spacing / Layout ──────────────────────────────────────────────────
      maxWidth: {
        content: '1200px',
      },
      borderRadius: {
        '2xl': '1rem',
        '3xl': '1.5rem',
      },
    },
  },
  plugins: [],
}

export default config
