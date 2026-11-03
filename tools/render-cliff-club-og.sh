#!/bin/sh
# Renders tools/cliff-club-og.html to cliffclub/img/og.jpg (1200x630) with headless Chrome.
set -e
cd "$(dirname "$0")/.."
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
OUT="$(mktemp -d)"
"$CHROME" --headless=new --disable-gpu --hide-scrollbars --force-device-scale-factor=1 \
  --window-size=1200,630 --virtual-time-budget=5000 \
  --screenshot="$OUT/og.png" "file://$PWD/tools/cliff-club-og.html" >/dev/null 2>&1
sips -s format jpeg -s formatOptions 88 "$OUT/og.png" --out cliffclub/img/og.jpg >/dev/null
rm -rf "$OUT"
echo "Wrote cliffclub/img/og.jpg"
