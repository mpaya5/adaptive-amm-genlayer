#!/usr/bin/env bash
# Stop GenLayer Studio Docker stack (keeps Ollama model cache on disk)
set -euo pipefail

if command -v genlayer &>/dev/null; then
  yes | genlayer stop 2>/dev/null || true
fi

GENLAYER_DIR="$(npm root -g 2>/dev/null)/genlayer"
if [ -d "$GENLAYER_DIR" ]; then
  cd "$GENLAYER_DIR"
  docker compose -p genlayer --profile frontend --profile ollama down 2>/dev/null || true
fi

echo "GenLayer Studio stopped."
