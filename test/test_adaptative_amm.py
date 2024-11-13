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

# Data for tests
symbol = "SUI/USDT"
order_book = {
    "bids": [
        [3.2, 10000],
        [3.198, 38000],
        [3.195, 45000]
    ],
    "asks": [
        [3.221, 6700],
        [3.224, 49000],
        [3.225, 70000]
    ]
}
current_price = 3.22
volume = 1000000
open_orders = [
    {"id": 1, "side": "buy", "price": 3.198, "amount": 20000},
    {"id": 2, "side": "buy", "price": 3.195, "amount": 37000},
    {"id": 3, "side": "sell", "price": 3.224, "amount": 25000},
    {"id": 4, "side": "sell", "price": 3.225, "amount": 55000}
]
balance = {"SUI": 30000000, "USDT": 12999000}
balance_percentage_to_use = 0.5
max_order_balance_percentage = 0.1
randomness_factor = 0.01
volatility_threshold = 0.02
max_order_size = 10000.0
min_order_size = 1000.0


def test_adaptive_amm_success():
    # Crear cuenta de prueba
    account_1 = create_new_account()

    # Configurar validadores para el test
    result = post_request_localhost(
        payload("sim_createRandomValidators", 5, 8, 12, ["openai"], ["gpt-4o"])
    ).json()
    assert has_success_status(result)

    # Desplegar el contrato y verificar el despliegue
    contract_code = open("contracts/amm_adaptative.py", "r").read()
    result_schema = post_request_localhost(
        payload("gen_getContractSchemaForCode", contract_code)
    ).json()
    assert has_success_status(result_schema)
    
    # Intento de despliegue del contrato
    try:
        contract_address, transaction_response_deploy = deploy_intelligent_contract(
            account_1,
            contract_code,
            "{}",
        )
        assert has_success_status(transaction_response_deploy)

    except KeyError as e:
        print("Error in deploy_intelligent_contract:", e)
        print("Full response:", transaction_response_deploy)

    # Intento de llamada al método resolve del contrato
    try:
        resolve_strategy_result = send_transaction(
            account_1,
            contract_address,
            "resolve",
            [
                symbol, balance_percentage_to_use, max_order_balance_percentage,
                randomness_factor, volatility_threshold, max_order_size, min_order_size
            ],
        )
        assert has_success_status(resolve_strategy_result)
        assert_dict_struct(
            resolve_strategy_result,
            execute_icontract_function_response_structure,
        )
    except KeyError as e:
        print("Error in send_transaction:", e)
        print("Transaction failed. No response to display.")
        return  

    # Resto de las validaciones del test
    strategy_result = resolve_strategy_result["output"]
    assert "cancel_orders" in strategy_result
    assert "new_orders" in strategy_result
    assert "reason_decision" in strategy_result

    # Validar los límites de balance en las órdenes
    for order in strategy_result["new_orders"]:
        assert order["amount"] <= max_order_balance_percentage * balance["SUI"]
        assert order["amount"] <= max_order_size

    # Verificar que las cancelaciones estén en open_orders
    for order_id in strategy_result["cancel_orders"]:
        assert any(order["id"] == order_id for order in open_orders)

    # Limpiar validadores después del test
    delete_validators_result = post_request_localhost(
        payload("sim_deleteAllValidators")
    ).json()
    assert has_success_status(delete_validators_result)