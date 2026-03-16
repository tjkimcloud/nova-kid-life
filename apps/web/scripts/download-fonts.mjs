/**
 * download-fonts.mjs
 * Downloads self-hosted woff2 font files from Google Fonts.
 * Run once after cloning: node apps/web/scripts/download-fonts.mjs
 *
 * Requires: Node 18+ (built-in fetch)
 * Output:   apps/web/src/fonts/
 */

import { writeFile, mkdir } from 'node:fs/promises'
import { fileURLToPath } from 'node:url'
import { join, dirname } from 'node:path'

const __dirname = dirname(fileURLToPath(import.meta.url))
const FONTS_DIR = join(__dirname, '..', 'src', 'fonts')

// Spoof a modern browser so Google Fonts returns woff2
const UA =
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

async function fetchLatinWoff2Url(family, weight) {
  const encoded = encodeURIComponent(family)
  const url = `https://fonts.googleapis.com/css2?family=${encoded}:wght@${weight}&display=swap`
  const res = await fetch(url, { headers: { 'User-Agent': UA } })
  if (!res.ok) throw new Error(`CSS fetch failed: ${res.status} for ${family} ${weight}`)
  const css = await res.text()
  // Latin subset is always the last @font-face block
  const matches = [...css.matchAll(/url\((https:\/\/fonts\.gstatic\.com\/[^)]+\.woff2)\)/g)]
  if (!matches.length) throw new Error(`No woff2 URL found for ${family} ${weight}`)
  return matches[matches.length - 1][1]
}

async function downloadFont(family, weight, filename) {
  process.stdout.write(`  Downloading ${filename} ...`)
  const woff2Url = await fetchLatinWoff2Url(family, weight)
  const res = await fetch(woff2Url, { headers: { 'User-Agent': UA } })
  if (!res.ok) throw new Error(`Font download failed: ${res.status}`)
  const buffer = Buffer.from(await res.arrayBuffer())
  await writeFile(join(FONTS_DIR, filename), buffer)
  console.log(` ${(buffer.length / 1024).toFixed(1)} KB`)
}

const FONTS = [
  ['Nunito', '600', 'Nunito-600.woff2'],
  ['Nunito', '700', 'Nunito-700.woff2'],
  ['Nunito', '800', 'Nunito-800.woff2'],
  ['Plus Jakarta Sans', '400', 'PlusJakartaSans-400.woff2'],
  ['Plus Jakarta Sans', '500', 'PlusJakartaSans-500.woff2'],
  ['Plus Jakarta Sans', '600', 'PlusJakartaSans-600.woff2'],
]

await mkdir(FONTS_DIR, { recursive: true })

console.log('\nDownloading Nunito (600, 700, 800)')
console.log('─'.repeat(40))
for (const [family, weight, filename] of FONTS.slice(0, 3)) {
  await downloadFont(family, weight, filename)
}

console.log('\nDownloading Plus Jakarta Sans (400, 500, 600)')
console.log('─'.repeat(40))
for (const [family, weight, filename] of FONTS.slice(3)) {
  await downloadFont(family, weight, filename)
}

console.log(`\nDone. Fonts saved to: apps/web/src/fonts/\n`)
