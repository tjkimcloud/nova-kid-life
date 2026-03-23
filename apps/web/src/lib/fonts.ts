import { Plus_Jakarta_Sans, DM_Sans } from 'next/font/google'

/**
 * Plus Jakarta Sans — display / headings
 * Weights: 400–800 (all needed for responsive scale)
 * CSS var: --font-plus-jakarta
 */
export const plusJakarta = Plus_Jakarta_Sans({
  subsets:  ['latin'],
  weight:   ['400', '500', '600', '700', '800'],
  variable: '--font-plus-jakarta',
  display:  'swap',
  preload:  true,
})

/**
 * DM Sans — body / UI text
 * Weights: 400, 500, 600
 * CSS var: --font-dm-sans
 */
export const dmSans = DM_Sans({
  subsets:  ['latin'],
  weight:   ['400', '500', '600'],
  variable: '--font-dm-sans',
  display:  'swap',
  preload:  true,
})

// Legacy alias — layout.tsx uses this name
export const nunito = plusJakarta
