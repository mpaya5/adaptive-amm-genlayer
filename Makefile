.PHONY: help setup dev studio-init studio-up studio-down studio-check \
        test test-deploy test-integration test-all frontend-dev frontend-demo \
        frontend-build screenshot

help:
	@echo "Adaptive AMM — common commands"
	@echo ""
	@echo "  make setup          Install Python + npm dependencies"
	@echo "  make dev            First-time bootstrap + start Studio"
	@echo "  make studio-init    One-time GenLayer init with Ollama"
	@echo "  make studio-up      Start GenLayer Studio (every session)"
	@echo "  make studio-down    Stop GenLayer Studio"
	@echo "  make studio-check   Verify JSON-RPC on :4000"
	@echo "  make test           Ollama validator smoke test"
	@echo "  make test-deploy    Deploy contract + demo state"
	@echo "  make test-integration  Live Binance + LLM resolve tests"
	@echo "  make frontend-dev   Vue dev server (needs deployed contract)"
	@echo "  make frontend-demo  Vue dev server with demo data (no deploy)"
	@echo "  make screenshot     Capture docs/assets/basic-amm-dashboard.png"
	@echo "  make frontend-build Production build"

setup:
	./scripts/setup.sh

dev:
	./scripts/dev.sh

studio-init:
	./scripts/studio-init-ollama.sh

studio-up:
	./scripts/studio-up.sh

studio-down:
	./scripts/studio-down.sh

studio-check:
	./scripts/studio-check.sh

test:
	@./scripts/studio-check.sh
	. venv/bin/activate && pytest test/test_adaptive_amm.py::test_ollama_validators_can_be_created -v

test-deploy:
	@./scripts/studio-check.sh
	. venv/bin/activate && pytest test/test_adaptive_amm.py::test_deploy_and_demo_state -v

test-integration:
	@./scripts/studio-check.sh
	. venv/bin/activate && pytest test/ -m integration -v

test-all:
	@./scripts/studio-check.sh
	. venv/bin/activate && pytest test/ -v

frontend-dev:
	cd app && npm run dev

frontend-demo:
	cd app && VITE_DEMO_MODE=true npm run dev

screenshot:
	./scripts/capture-dashboard-screenshot.sh

frontend-build:
	cd app && npm run build
