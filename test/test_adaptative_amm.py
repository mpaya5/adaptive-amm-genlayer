from tools.accounts import create_new_account
from tools.request import (
    deploy_intelligent_contract,
    send_transaction,
    call_contract_method,
    payload,
    post_request_localhost,
)
from tools.structure import execute_icontract_function_response_structure
from tools.response import (
    assert_dict_struct,
    has_success_status,
)

import json
import pytest

symbol = "SUI/USDT"
open_orders = [
    {"id": 1, "side": "sell", "price": 3.60, "amount": 5000},
    {"id": 2, "side": "sell", "price": 3.40, "amount": 10000},
    {"id": 3, "side": "sell", "price": 3.20, "amount": 15000},
    {"id": 4, "side": "buy", "price": 3.00, "amount": 20000},
    {"id": 5, "side": "buy", "price": 2.80, "amount": 10000},
    {"id": 6, "side": "buy", "price": 2.60, "amount": 5000},
]
balance = {"SUI": 300000, "USDT": 12999}
max_order_balance_percentage = 0.1
max_order_size = 10000.0


def _decode_call_result(raw):
    if raw is None:
        return None
    if isinstance(raw, (dict, list)):
        return raw
    if isinstance(raw, str):
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return raw
    return raw


def test_ollama_validators_can_be_created(validator_llm_config):
    """Smoke test: Studio accepts Ollama validators without paid API keys."""
    provider, model = validator_llm_config

    result = post_request_localhost(
        payload("sim_createRandomValidators", 3, 5, 10, [provider], [model])
    ).json()
    assert has_success_status(result)
    assert len(result["result"]) == 3
    assert all(v["provider"] == provider and v["model"] == model for v in result["result"])

    cleanup = post_request_localhost(payload("sim_deleteAllValidators")).json()
    assert has_success_status(cleanup)


@pytest.fixture
def deployed_contract(validator_llm_config):
    account_1 = create_new_account()
    provider, model = validator_llm_config

    result = post_request_localhost(
        payload("sim_createRandomValidators", 5, 8, 12, [provider], [model])
    ).json()
    assert has_success_status(result)

    contract_code = open("contracts/amm_adaptative.py", "r").read()
    assert contract_code.startswith('# { "Depends": "py-genlayer:')
    assert "gl.nondet.web.get" in contract_code

    contract_address, deploy_response = deploy_intelligent_contract(
        account_1,
        contract_code,
        '{"symbol": "SUI/USDT", "exchange_symbol": "SUIUSDT", "data_source": "binance"}',
    )
    assert has_success_status(deploy_response)

    yield account_1, contract_address

    delete_validators_result = post_request_localhost(
        payload("sim_deleteAllValidators")
    ).json()
    assert has_success_status(delete_validators_result)


def test_deploy_and_demo_state(deployed_contract):
    account_1, contract_address = deployed_contract

    price = _decode_call_result(
        call_contract_method(contract_address, account_1, "get_current_price", [])
    )
    assert price == 3.22

    orders = _decode_call_result(
        call_contract_method(contract_address, account_1, "get_open_orders", [])
    )
    assert len(orders) == 6

    data_source = _decode_call_result(
        call_contract_method(contract_address, account_1, "get_data_source", [])
    )
    assert data_source == "binance"


@pytest.mark.integration
def test_refresh_market_data_live(deployed_contract):
    """Requires GenLayer Studio with outbound network access to Binance API."""
    account_1, contract_address = deployed_contract

    refresh_result = send_transaction(
        account_1, contract_address, "refresh_market_data", []
    )
    assert has_success_status(refresh_result)

    price = _decode_call_result(
        call_contract_method(contract_address, account_1, "get_current_price", [])
    )
    assert float(price) > 0

    order_book = _decode_call_result(
        call_contract_method(contract_address, account_1, "get_order_book", [])
    )
    assert len(order_book["bids"]) >= 1
    assert len(order_book["asks"]) >= 1


@pytest.mark.integration
def test_resolve_with_live_market(deployed_contract):
    """Full flow: live web fetch + LLM resolve. Requires Studio + Ollama validators."""
    account_1, contract_address = deployed_contract

    resolve_result = send_transaction(account_1, contract_address, "resolve", [])
    assert has_success_status(resolve_result)
    assert_dict_struct(resolve_result, execute_icontract_function_response_structure)

    strategy_result = _decode_call_result(
        call_contract_method(contract_address, account_1, "get_resolve_response", [])
    )
    assert isinstance(strategy_result, dict)
    assert "cancel_orders" in strategy_result
    assert "new_orders" in strategy_result
    assert "reason_decision" in strategy_result

    for order in strategy_result["new_orders"]:
        assert order["amount"] <= max_order_balance_percentage * balance["SUI"]
        assert order["amount"] <= max_order_size

    for order_id in strategy_result["cancel_orders"]:
        assert any(order["id"] == order_id for order in open_orders)
