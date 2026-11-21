#!/bin/sh
# Renders tools/shop-small-social.html to smallbusinesssaturday/social/post.jpg (1080x1350)
# and story.jpg (1080x1920) with headless Chrome.
set -e
cd "$(dirname "$0")/.."
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
OUT="$(mktemp -d)"
render() {
  "$CHROME" --headless=new --disable-gpu --hide-scrollbars --force-device-scale-factor=1 \
    --window-size="$2" --virtual-time-budget=5000 \
    --screenshot="$OUT/$1.png" "file://$PWD/tools/shop-small-social.html#$1" >/dev/null 2>&1
  sips -s format jpeg -s formatOptions 92 "$OUT/$1.png" --out "smallbusinesssaturday/social/$1.jpg" >/dev/null
  echo "Wrote smallbusinesssaturday/social/$1.jpg"
}
render post 1080,1350
render story 1080,1920
rm -rf "$OUT"
