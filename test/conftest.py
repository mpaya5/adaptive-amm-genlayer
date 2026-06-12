import os

import pytest
import requests
from dotenv import load_dotenv

load_dotenv()

RPC_PROTOCOL = os.getenv("RPCPROTOCOL", "http")
RPC_HOST = os.getenv("RPCHOST", "localhost")
RPC_PORT = os.getenv("RPCPORT", "4000")
RPC_URL = f"{RPC_PROTOCOL}://{RPC_HOST}:{RPC_PORT}/api"

DEFAULT_VALIDATOR_PROVIDER = os.getenv("GENLAYER_VALIDATOR_PROVIDER", "ollama")
DEFAULT_VALIDATOR_MODEL = os.getenv("GENLAYER_VALIDATOR_MODEL", "llama3")


def is_studio_running() -> bool:
    try:
        response = requests.post(
            RPC_URL,
            json={"jsonrpc": "2.0", "method": "eth_chainId", "params": [], "id": 1},
            timeout=3,
        )
        return response.status_code == 200 and "result" in response.json()
    except requests.RequestException:
        return False


@pytest.fixture(scope="session")
def validator_llm_config(require_studio):
    return DEFAULT_VALIDATOR_PROVIDER, DEFAULT_VALIDATOR_MODEL


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "integration: requires Studio, outbound Binance access, and Ollama validators",
    )


@pytest.fixture(scope="session")
def require_studio():
    if not is_studio_running():
        pytest.skip(
            f"GenLayer Studio is not running at {RPC_URL}. "
            "Start it with: ./scripts/studio-up.sh"
        )
