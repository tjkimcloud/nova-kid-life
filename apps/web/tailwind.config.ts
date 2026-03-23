import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      // ── Creamsicle Modern Palette ──────────────────────────────────────────
      // primary = orange family | secondary = warm neutral family
      // Values mirror DESIGN_SYSTEM.md and CSS vars in globals.css.
      // Hardcoded so Tailwind opacity modifiers (bg-primary-500/50) work.
      colors: {
        primary: {
          50:  '#FFF0E6',  // orange-pale
          100: '#FFD9C0',
          200: '#FFC09A',
          300: '#FF9E6E',
          400: '#FF8C55',  // orange-soft
          500: '#E85D1A',  // orange — main brand CTA
          600: '#D44E10',
          700: '#B8410D',
          800: '#92400E',
          900: '#7A3509',
          950: '#5C2807',
        },
        secondary: {
          50:  '#FFF8F2',  // --bg  (page background)
          100: '#F5EDE0',  // --bg2 (card footers)
          200: '#EDE0CF',  // --bg3 / --border
          300: '#D4C0AA',
          400: '#A89588',  // --text3
          500: '#6B5E54',  // --text2
          600: '#554A42',
          700: '#3D342E',
          800: '#2A221D',
          900: '#1C1714',  // --text (headings, body)
          950: '#0E0B09',
        },
      },
      // ── Typography ────────────────────────────────────────────────────────
      fontFamily: {
        heading: ['var(--font-plus-jakarta)', 'Plus Jakarta Sans', 'ui-sans-serif', 'sans-serif'],
        body:    ['var(--font-dm-sans)',       'DM Sans',           'ui-sans-serif', 'sans-serif'],
      },
      // ── Spacing / Radius ──────────────────────────────────────────────────
      maxWidth: {
        content: '900px',
      },
      borderRadius: {
        DEFAULT: '10px',   // --radius-sm
        md:      '10px',
        lg:      '16px',   // --radius
        xl:      '16px',
        '2xl':   '22px',   // --radius-lg (event cards)
        '3xl':   '22px',
      },
      // ── Shadows ───────────────────────────────────────────────────────────
      boxShadow: {
        sm:     '0 1px 4px rgba(0,0,0,0.06)',
        DEFAULT: '0 4px 20px rgba(0,0,0,0.08)',
        md:     '0 4px 20px rgba(0,0,0,0.08)',
        lg:     '0 8px 30px rgba(0,0,0,0.10)',
        orange: '0 6px 20px rgba(232,93,26,0.28)',
      },
    },
  },
  plugins: [],
}

export default config
