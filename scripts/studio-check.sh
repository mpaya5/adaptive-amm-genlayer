#!/usr/bin/env bash
# Verify GenLayer Studio JSON-RPC responds on localhost:4000
set -euo pipefail

RPC_URL="${RPC_URL:-http://localhost:4000/api}"

response=$(curl -sf -X POST "$RPC_URL" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"eth_chainId","params":[],"id":1}' \
  2>/dev/null || true)

if [ -n "$response" ]; then
  echo "GenLayer Studio is up at $RPC_URL"
  echo "  Response: $response"
  exit 0
fi

echo "GenLayer Studio is NOT running at $RPC_URL"
echo ""
echo "Start it with:"
echo "  ./scripts/studio-up.sh"
echo "  # or: make studio-up"
echo ""
echo "First time on this machine:"
echo "  ./scripts/studio-init-ollama.sh"
echo "  # or: make studio-init"
echo ""
echo "Studio UI: http://localhost:8080"
exit 1
