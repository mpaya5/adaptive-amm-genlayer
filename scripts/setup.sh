#!/usr/bin/env bash
# Bootstrap Python venv, backend deps, and Vue frontend
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "==> Python venv + dependencies"
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

if [ ! -f .env ]; then
  cp .env.example .env
  echo "    Created .env from .env.example"
fi

echo "==> Frontend (app/)"
cd app
npm install
if [ ! -f .env ]; then
  cp .env.example .env
  echo "    Created app/.env — set VITE_CONTRACT_ADDRESS after deploy"
fi

cd "$ROOT"
chmod +x scripts/*.sh

echo ""
echo "Setup complete."
echo ""
echo "Next — start GenLayer Studio (required for tests and the dApp):"
echo "  make studio-init   # first time only"
echo "  make studio-up     # every dev session"
echo ""
echo "Then run tests:"
echo "  source venv/bin/activate"
echo "  make test"
