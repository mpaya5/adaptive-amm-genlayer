#!/usr/bin/env bash
# Full dev bootstrap: setup (if needed) + Studio + smoke test
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [ ! -d venv ]; then
  ./scripts/setup.sh
fi

if ! docker ps --format '{{.Names}}' 2>/dev/null | grep -q '^genlayer-jsonrpc-1$'; then
  if ! docker ps -a --format '{{.Names}}' 2>/dev/null | grep -q '^genlayer-ollama$'; then
    echo "==> First-time Studio init (Ollama)..."
    ./scripts/studio-init-ollama.sh
  else
    ./scripts/studio-up.sh
  fi
else
  ./scripts/studio-check.sh || ./scripts/studio-up.sh
fi

./scripts/studio-check.sh

echo ""
echo "Ready for development."
echo "  Studio UI : http://localhost:8080"
echo "  JSON-RPC  : http://localhost:4000/api"
echo "  Tests     : source venv/bin/activate && make test"
echo "  Frontend  : make frontend-dev"
