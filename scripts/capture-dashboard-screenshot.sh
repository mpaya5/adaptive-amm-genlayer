#!/usr/bin/env bash
# Start Vue dashboard in demo mode and save docs/assets/basic-amm-dashboard.png
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
APP_DIR="$ROOT/app"
PORT="${DASHBOARD_PORT:-5173}"
URL="http://127.0.0.1:${PORT}"

cd "$APP_DIR"

if [ ! -d node_modules ]; then
  npm install
fi

npm install --no-save playwright@1.49.1 >/dev/null
npx playwright install chromium >/dev/null

export VITE_DEMO_MODE=true
export VITE_CONTRACT_ADDRESS=0x0000000000000000000000000000000000000000

npm run dev -- --host 127.0.0.1 --port "$PORT" &
DEV_PID=$!
trap 'kill $DEV_PID 2>/dev/null || true' EXIT

for _ in $(seq 1 30); do
  if curl -sf "$URL" >/dev/null 2>&1; then
    break
  fi
  sleep 1
done

sleep 3
mkdir -p "$ROOT/docs/assets"
npx playwright screenshot \
  --full-page \
  --viewport-size=1280,900 \
  --wait-for-timeout=3000 \
  "$URL" \
  "$ROOT/docs/assets/basic-amm-dashboard.png"
echo "Screenshot written to docs/assets/basic-amm-dashboard.png"
