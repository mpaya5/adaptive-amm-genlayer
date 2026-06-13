# v0.1.0
# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

from genlayer import *
import json
from dataclasses import dataclass

# Public Binance endpoints - no API key required (read-only market data)
BINANCE_DEPTH_URL = "https://api.binance.com/api/v3/depth?symbol={symbol}&limit=5"
BINANCE_TICKER_URL = "https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}"
MARKET_PRICE_TOLERANCE = 0.02  # 2% - validators may fetch at slightly different times


@allow_storage
@dataclass
class Order:
    id: u32
    side: str
    price: float
    amount: float


class AdaptiveAMM(gl.Contract):
    """
    Adaptive AMM with live order-book ingestion via GenLayer web connectivity.
    Market data is fetched on-chain with gl.nondet.web.get + Equivalence Principle.
    """

    symbol: str
    exchange_symbol: str
    data_source: str
    balance_percentage_to_use: float
    max_order_balance_percentage: float
    randomness_factor: float
    volatility_threshold: float
    max_order_size: float
    min_order_size: float
    current_price: float
    volume: float
    balance_sui: float
    balance_usdt: float
    order_book_json: str
    open_orders: DynArray[Order]
    reason_decision: str
    last_cancel_orders: DynArray[u32]
    last_new_orders: DynArray[Order]

    def __init__(
        self,
        symbol: str = "SUI/USDT",
        exchange_symbol: str = "SUIUSDT",
        data_source: str = "binance",
        balance_percentage_to_use: float = 0.5,
        max_order_balance_percentage: float = 0.1,
        randomness_factor: float = 0.01,
        volatility_threshold: float = 0.02,
        max_order_size: float = 10000.0,
        min_order_size: float = 1000.0,
    ):
        self.symbol = symbol
        self.exchange_symbol = exchange_symbol
        self.data_source = data_source
        self.balance_percentage_to_use = balance_percentage_to_use
        self.max_order_balance_percentage = max_order_balance_percentage
        self.randomness_factor = randomness_factor
        self.volatility_threshold = volatility_threshold
        self.max_order_size = max_order_size
        self.min_order_size = min_order_size
        self.current_price = 3.22
        self.volume = 1000000.0
        self.balance_sui = 300000.0
        self.balance_usdt = 12999.0
        self.order_book_json = json.dumps(AdaptiveAMM._default_order_book())
        self.reason_decision = ""

        orders = gl.storage.inmem_allocate(DynArray[Order])
        for order_id, side, price, amount in [
            (u32(1), "sell", 3.60, 5000.0),
            (u32(2), "sell", 3.40, 10000.0),
            (u32(3), "sell", 3.20, 15000.0),
            (u32(4), "buy", 3.00, 20000.0),
            (u32(5), "buy", 2.80, 10000.0),
            (u32(6), "buy", 2.60, 5000.0),
        ]:
            orders.append(Order(order_id, side, price, amount))
        self.open_orders = orders
        self.last_cancel_orders = gl.storage.inmem_allocate(DynArray[u32])
        self.last_new_orders = gl.storage.inmem_allocate(DynArray[Order])

    @staticmethod
    def _default_order_book() -> dict:
        return {
            "bids": [[3.00, 20000.0], [2.80, 10000.0], [2.60, 5000.0]],
            "asks": [[3.20, 15000.0], [3.40, 10000.0], [3.60, 5000.0]],
        }

    @staticmethod
    def _fetch_live_market_data(exchange_symbol: str) -> dict:
        depth_url = BINANCE_DEPTH_URL.format(symbol=exchange_symbol)
        ticker_url = BINANCE_TICKER_URL.format(symbol=exchange_symbol)

        depth_resp = gl.nondet.web.get(depth_url)
        ticker_resp = gl.nondet.web.get(ticker_url)

        depth = json.loads(depth_resp.body.decode("utf-8"))
        ticker = json.loads(ticker_resp.body.decode("utf-8"))

        bids = [[float(price), float(qty)] for price, qty in depth.get("bids", [])[:3]]
        asks = [[float(price), float(qty)] for price, qty in depth.get("asks", [])[:3]]

        if not bids or not asks:
            raise gl.vm.UserError("[EXTERNAL] Empty order book returned by exchange API")

        return {
            "bids": bids,
            "asks": asks,
            "current_price": float(ticker["lastPrice"]),
            "volume": float(ticker["quoteVolume"]),
        }

    @staticmethod
    def _market_data_matches(leader: dict, validator: dict, tolerance: float) -> bool:
        if not leader.get("bids") or not leader.get("asks"):
            return False
        if not validator.get("bids") or not validator.get("asks"):
            return False

        for field in ("current_price",):
            a = float(leader[field])
            b = float(validator[field])
            if b == 0.0:
                if a != 0.0:
                    return False
            elif abs(a - b) / abs(b) > tolerance:
                return False

        leader_best_bid = float(leader["bids"][0][0])
        validator_best_bid = float(validator["bids"][0][0])
        leader_best_ask = float(leader["asks"][0][0])
        validator_best_ask = float(validator["asks"][0][0])

        for a, b in (
            (leader_best_bid, validator_best_bid),
            (leader_best_ask, validator_best_ask),
        ):
            if b == 0.0:
                if a != 0.0:
                    return False
            elif abs(a - b) / abs(b) > tolerance:
                return False

        return True

    def _run_live_market_fetch(self) -> dict:
        exchange_symbol = self.exchange_symbol
        tolerance = MARKET_PRICE_TOLERANCE

        def leader_fn():
            return AdaptiveAMM._fetch_live_market_data(exchange_symbol)

        def validator_fn(leader_result) -> bool:
            if not isinstance(leader_result, gl.vm.Return):
                return False
            validator_data = leader_fn()
            return AdaptiveAMM._market_data_matches(
                leader_result.calldata, validator_data, tolerance
            )

        return gl.vm.run_nondet_unsafe(leader_fn, validator_fn)

    def _apply_market_data(self, data: dict) -> None:
        self.order_book_json = json.dumps(
            {"bids": data["bids"], "asks": data["asks"]}
        )
        self.current_price = float(data["current_price"])
        self.volume = float(data["volume"])

    def _parsed_order_book(self) -> dict:
        if not self.order_book_json:
            return {"bids": [], "asks": []}
        return json.loads(self.order_book_json)

    def _market_snapshot(self) -> dict:
        open_orders = []
        for order in self.open_orders:
            open_orders.append(
                {
                    "id": order.id,
                    "side": order.side,
                    "price": order.price,
                    "amount": order.amount,
                }
            )
        return {
            "symbol": self.symbol,
            "data_source": self.data_source,
            "order_book": self._parsed_order_book(),
            "current_price": self.current_price,
            "volume": self.volume,
            "open_orders": open_orders,
            "balance": {"SUI": self.balance_sui, "USDT": self.balance_usdt},
            "balance_percentage_to_use": self.balance_percentage_to_use,
            "max_order_balance_percentage": self.max_order_balance_percentage,
            "volatility_threshold": self.volatility_threshold,
            "max_order_size": self.max_order_size,
            "min_order_size": self.min_order_size,
            "randomness_factor": self.randomness_factor,
        }

    def _build_prompt(self, market: dict) -> str:
        return f"""You are an adaptive market maker for '{market["symbol"]}' using live data from {market["data_source"]}.
Analyze the market data and return JSON with recommended order cancellations and placements.

Market Data:
- symbol: {market["symbol"]}
- data_source: {market["data_source"]}
- order_book (live): {json.dumps(market["order_book"])}
- current_price: {market["current_price"]}
- volume: {market["volume"]}
- open_orders: {json.dumps(market["open_orders"])}
- balance: {json.dumps(market["balance"])}
- balance_percentage_to_use: {market["balance_percentage_to_use"]}
- max_order_balance_percentage: {market["max_order_balance_percentage"]}
- volatility_threshold: {market["volatility_threshold"]}
- max_order_size: {market["max_order_size"]}
- min_order_size: {market["min_order_size"]}
- randomness_factor: {market["randomness_factor"]}

Rules:
1. Respect balance and per-order size constraints.
2. cancel_orders must reference existing order IDs only.
3. new_orders must use side "buy" or "sell" with positive price and amount.
4. Use the live order book to place competitive bids and asks.

Return JSON:
{{
  "cancel_orders": [int],
  "new_orders": [{{"side": "buy"|"sell", "price": float, "amount": float}}],
  "reason_decision": "brief explanation referencing live market conditions"
}}"""

    @staticmethod
    def _is_valid_response(data, max_order_size: float, min_order_size: float) -> bool:
        if not isinstance(data, dict):
            return False
        for key in ("cancel_orders", "new_orders", "reason_decision"):
            if key not in data:
                return False
        if not isinstance(data["cancel_orders"], list):
            return False
        if not isinstance(data["new_orders"], list):
            return False
        if not isinstance(data["reason_decision"], str):
            return False
        for order in data["new_orders"]:
            if not isinstance(order, dict):
                return False
            if order.get("side") not in ("buy", "sell"):
                return False
            if float(order.get("amount", 0)) <= 0:
                return False
            if float(order.get("price", 0)) <= 0:
                return False
            if float(order["amount"]) > max_order_size:
                return False
            if float(order["amount"]) < min_order_size:
                return False
        return True

    def _apply_resolve(self, result: dict) -> None:
        cancel_ids = {u32(cid) for cid in result["cancel_orders"]}
        updated = gl.storage.inmem_allocate(DynArray[Order])
        max_id = u32(0)

        for order in self.open_orders:
            if order.id not in cancel_ids:
                updated.append(order)
                if order.id > max_id:
                    max_id = order.id

        next_id = max_id + u32(1)
        for new_order in result["new_orders"]:
            updated.append(
                Order(
                    id=next_id,
                    side=new_order["side"],
                    price=float(new_order["price"]),
                    amount=float(new_order["amount"]),
                )
            )
            next_id = next_id + u32(1)

        self.open_orders = updated
        self.reason_decision = result["reason_decision"]

        self.last_cancel_orders = gl.storage.inmem_allocate(DynArray[u32])
        for cancel_id in result["cancel_orders"]:
            self.last_cancel_orders.append(u32(cancel_id))

        self.last_new_orders = gl.storage.inmem_allocate(DynArray[Order])
        for new_order in result["new_orders"]:
            self.last_new_orders.append(
                Order(
                    id=u32(0),
                    side=new_order["side"],
                    price=float(new_order["price"]),
                    amount=float(new_order["amount"]),
                )
            )

    @gl.public.view
    def get_symbol(self) -> str:
        return self.symbol

    @gl.public.view
    def get_data_source(self) -> str:
        return self.data_source

    @gl.public.view
    def get_order_book(self) -> dict:
        return self._parsed_order_book()

    @gl.public.view
    def get_current_price(self) -> float:
        return self.current_price

    @gl.public.view
    def get_volume(self) -> float:
        return self.volume

    @gl.public.view
    def get_open_orders(self) -> list:
        orders = []
        for order in self.open_orders:
            orders.append(
                {
                    "id": order.id,
                    "side": order.side,
                    "price": order.price,
                    "amount": order.amount,
                }
            )
        return orders

    @gl.public.view
    def get_balance(self) -> dict:
        return {"SUI": self.balance_sui, "USDT": self.balance_usdt}

    @gl.public.view
    def get_resolve_response(self) -> dict:
        new_orders = []
        for order in self.last_new_orders:
            new_orders.append(
                {
                    "side": order.side,
                    "price": order.price,
                    "amount": order.amount,
                }
            )
        cancel_orders = [int(cancel_id) for cancel_id in self.last_cancel_orders]
        return {
            "cancel_orders": cancel_orders,
            "new_orders": new_orders,
            "reason_decision": self.reason_decision,
        }

    @gl.public.write
    def refresh_market_data(self) -> None:
        """Fetch live order book, price and volume from Binance via gl.nondet.web.get."""
        self._apply_market_data(self._run_live_market_fetch())

    @gl.public.write
    def resolve(self) -> None:
        """Refresh live market data, then run LLM market-making with validator consensus."""
        self._apply_market_data(self._run_live_market_fetch())

        market = self._market_snapshot()
        prompt = self._build_prompt(market)
        max_order_size = self.max_order_size
        min_order_size = self.min_order_size

        def leader_fn():
            return gl.nondet.exec_prompt(prompt, response_format="json")

        def validator_fn(leader_result) -> bool:
            if not isinstance(leader_result, gl.vm.Return):
                return False
            leader_data = leader_result.calldata
            if not AdaptiveAMM._is_valid_response(
                leader_data, max_order_size, min_order_size
            ):
                return False
            validator_data = leader_fn()
            if not AdaptiveAMM._is_valid_response(
                validator_data, max_order_size, min_order_size
            ):
                return False
            return sorted(leader_data["cancel_orders"]) == sorted(
                validator_data["cancel_orders"]
            ) and len(leader_data["new_orders"]) == len(validator_data["new_orders"])

        result = gl.vm.run_nondet_unsafe(leader_fn, validator_fn)
        self._apply_resolve(result)
