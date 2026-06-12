#!/usr/bin/env bash
# Start GenLayer Studio localnet with Ollama — no paid LLM API keys
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OLLAMA_MODEL="${GENLAYER_VALIDATOR_MODEL:-llama3}"

echo "==> Checking prerequisites..."
command -v docker >/dev/null 2>&1 || {
  echo "Docker not found. Install: https://docs.docker.com/engine/install/"
  exit 1
}

if ! command -v genlayer &>/dev/null; then
  echo "==> Installing GenLayer CLI (npm install -g genlayer)..."
  npm install -g genlayer
fi

echo "==> Starting GenLayer Studio with Ollama..."
echo "    JSON-RPC : http://localhost:4000/api"
echo "    Studio UI: http://localhost:8080"
echo "    LLM        : ollama / ${OLLAMA_MODEL}"
echo ""

if ! docker ps --format '{{.Names}}' 2>/dev/null | grep -q '^genlayer-ollama$'; then
  echo "    First time? Run: ./scripts/studio-init-ollama.sh"
  echo ""
fi

yes | genlayer up --ollama 2>/dev/null || genlayer up --ollama

echo "==> Waiting for JSON-RPC..."
for _ in $(seq 1 60); do
  if curl -sf -X POST http://localhost:4000/api \
    -H "Content-Type: application/json" \
    -d '{"jsonrpc":"2.0","method":"eth_chainId","params":[],"id":1}' >/dev/null 2>&1; then
    break
  fi
  sleep 2
done

if ! docker ps --format '{{.Names}}' 2>/dev/null | grep -q '^genlayer-ollama$'; then
  echo "genlayer-ollama container is not running."
  echo "Run once: ./scripts/studio-init-ollama.sh"
  exit 1
fi

echo "==> Ensuring Ollama model (${OLLAMA_MODEL})..."
if ! docker exec genlayer-ollama ollama list 2>/dev/null | awk 'NR>1 {print $1}' | grep -qx "${OLLAMA_MODEL}"; then
  echo "    Pulling ${OLLAMA_MODEL} (may take several minutes, ~4.7 GB)..."
  docker exec genlayer-ollama ollama pull "${OLLAMA_MODEL}"
fi

echo ""
echo "GenLayer Studio is ready (Ollama)."
