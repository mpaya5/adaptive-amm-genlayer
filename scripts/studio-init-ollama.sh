#!/usr/bin/env bash
# One-time GenLayer Studio init with local Ollama (llama3) — no paid API keys
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

command -v genlayer >/dev/null 2>&1 || {
  echo "genlayer CLI not found. Run: npm install -g genlayer"
  exit 1
}

if [ ! -d venv ]; then
  echo "venv not found. Run first: ./scripts/setup.sh"
  exit 1
}

source venv/bin/activate
pip install -q pexpect

echo "==> Initializing GenLayer Studio (Ollama + localnet v0.69.2)..."
echo "    This resets GenLayer Docker state. Confirm when prompted."
echo ""

python3 << 'PY'
import pexpect
import sys

child = pexpect.spawn(
    "genlayer init --ollama --numValidators 5 --localnet-version v0.69.2",
    encoding="utf-8",
    timeout=900,
)
child.logfile = sys.stdout
child.expect("Do you want to continue")
child.sendline("y")
child.expect("Select which LLM providers")
child.send(" ")
child.sendline("")
child.expect(pexpect.EOF)
if child.exitstatus not in (None, 0):
    raise SystemExit(child.exitstatus or 1)
PY

echo ""
echo "GenLayer Studio initialized with Ollama (llama3)."
echo "Studio UI: http://localhost:8080"
echo "JSON-RPC : http://localhost:4000/api"
