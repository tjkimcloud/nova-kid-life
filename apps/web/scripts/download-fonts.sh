#!/usr/bin/env bash
# download-fonts.sh
# Downloads self-hosted woff2 font files from Google Fonts.
# Run once after cloning: bash apps/web/scripts/download-fonts.sh
#
# Output: apps/web/src/fonts/
#   Nunito-600.woff2
#   Nunito-700.woff2
#   Nunito-800.woff2
#   PlusJakartaSans-400.woff2
#   PlusJakartaSans-500.woff2
#   PlusJakartaSans-600.woff2

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FONTS_DIR="$SCRIPT_DIR/../src/fonts"
mkdir -p "$FONTS_DIR"

# Spoof a modern browser UA so Google Fonts returns woff2 (not woff/ttf)
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# fetch_latin_url <google-fonts-css2-url> → woff2 URL for the latin subset
# Google Fonts CSS lists subsets as @font-face blocks; latin is always last.
fetch_latin_url() {
  local css_url="$1"
  curl -fsSL -A "$UA" "$css_url" \
    | grep -oE 'https://fonts\.gstatic\.com/[^ )]+\.woff2' \
    | tail -1
}

download_weight() {
  local family_encoded="$1"   # URL-encoded family name
  local weight="$2"
  local output_name="$3"

  local css_url="https://fonts.googleapis.com/css2?family=${family_encoded}:wght@${weight}&display=swap"
  local woff2_url
  woff2_url=$(fetch_latin_url "$css_url")

  if [ -z "$woff2_url" ]; then
    echo "  ERROR: could not resolve woff2 URL for $output_name" >&2
    return 1
  fi

  echo "  Downloading $output_name..."
  curl -fsSL -o "$FONTS_DIR/$output_name" "$woff2_url"
}

echo "──────────────────────────────────────────"
echo " Downloading Nunito (600, 700, 800)"
echo "──────────────────────────────────────────"
download_weight "Nunito" "600" "Nunito-600.woff2"
download_weight "Nunito" "700" "Nunito-700.woff2"
download_weight "Nunito" "800" "Nunito-800.woff2"

echo ""
echo "──────────────────────────────────────────"
echo " Downloading Plus Jakarta Sans (400, 500, 600)"
echo "──────────────────────────────────────────"
download_weight "Plus+Jakarta+Sans" "400" "PlusJakartaSans-400.woff2"
download_weight "Plus+Jakarta+Sans" "500" "PlusJakartaSans-500.woff2"
download_weight "Plus+Jakarta+Sans" "600" "PlusJakartaSans-600.woff2"

echo ""
echo "✓ Done. Fonts saved to: $FONTS_DIR"
echo ""
ls -lh "$FONTS_DIR"
