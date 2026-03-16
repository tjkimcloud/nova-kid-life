import localFont from 'next/font/local'

/**
 * Nunito — headings and UI elements
 * Weights: 600 (SemiBold), 700 (Bold), 800 (ExtraBold)
 *
 * Font files live at src/fonts/. Download them once with:
 *   bash apps/web/scripts/download-fonts.sh
 */
export const nunito = localFont({
  src: [
    {
      path: '../fonts/Nunito-600.woff2',
      weight: '600',
      style: 'normal',
    },
    {
      path: '../fonts/Nunito-700.woff2',
      weight: '700',
      style: 'normal',
    },
    {
      path: '../fonts/Nunito-800.woff2',
      weight: '800',
      style: 'normal',
    },
  ],
  variable: '--font-nunito',
  display: 'swap',
  preload: true,
  fallback: ['ui-rounded', 'Helvetica Neue', 'Arial', 'sans-serif'],
})

/**
 * Plus Jakarta Sans — body text and captions
 * Weights: 400 (Regular), 500 (Medium), 600 (SemiBold)
 *
 * Font files live at src/fonts/. Download them once with:
 *   bash apps/web/scripts/download-fonts.sh
 */
export const plusJakarta = localFont({
  src: [
    {
      path: '../fonts/PlusJakartaSans-400.woff2',
      weight: '400',
      style: 'normal',
    },
    {
      path: '../fonts/PlusJakartaSans-500.woff2',
      weight: '500',
      style: 'normal',
    },
    {
      path: '../fonts/PlusJakartaSans-600.woff2',
      weight: '600',
      style: 'normal',
    },
  ],
  variable: '--font-plus-jakarta',
  display: 'swap',
  preload: true,
  fallback: ['ui-sans-serif', 'system-ui', 'Arial', 'sans-serif'],
})
