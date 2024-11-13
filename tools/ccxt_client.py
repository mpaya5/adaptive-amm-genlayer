import ccxt.async_support as ccxt
import asyncio
import random

class CCXTSimulator:
    def __init__(self, symbol: str, exchange: str):
        """
        Initializes the CCXTSimulator class with a trading pair symbol and exchange.

        Args:
            symbol (str): The trading pair symbol (e.g., 'BTC/USDT').
            exchange (str): The name of the exchange (e.g., 'binance').
        """
        self.symbol = symbol
        self.exchange_name = exchange
        self.exchange_class = getattr(ccxt, self.exchange_name)
        self.exchange = self.exchange_class()

    # Retrieve market data functions
    async def get_order_book(self):
        """
        Retrieves the order book data.
        """
        await self.exchange.load_markets()
        return await self.exchange.fetch_order_book(self.symbol)

    async def get_ticker(self):
        """
        Retrieves the ticker of the asset.
        """
        return await self.exchange.fetch_ticker(self.symbol)

    async def get_current_price(self):
        """
        Retrieves the current price of the asset.
        """
        ticker = await self.get_ticker()
        return ticker["last"] if ticker else None

    async def get_volume(self):
        """
        Retrieves the 24-hour trading volume for the asset symbol.
        """
        ticker = await self.get_ticker()
        return ticker["quoteVolume"] if ticker else random.uniform(500000, 1000000)

    async def get_open_orders(self):
        """
        Simulates creating open orders close to the current price.
        """
        current_price = await self.get_current_price()
        num_orders = random.randint(3, 7)
        orders = []
        for i in range(num_orders):
            side = "buy" if i % 2 == 0 else "sell"
            price_offset = random.uniform(-0.005, 0.005)  # Slight offset from current price
            price = current_price * (1 + price_offset if side == "buy" else 1 - price_offset)
            amount = random.uniform(5000, 20000)  # Random amount
            orders.append({
                "id": i + 1,
                "side": side,
                "price": round(price, 4),
                "amount": round(amount, 2)
            })
        return orders
    
    def get_balance(self):
        """
        Simulates a balance for the symbol and its quote asset.
        """
        return {
            self.symbol.split("/")[0]: random.uniform(200000, 500000),  
            self.symbol.split("/")[1]: random.uniform(100000, 300000)  
        }

    async def close_connection(self):
        """
        Closes the exchange connection.
        """
        await self.exchange.close()