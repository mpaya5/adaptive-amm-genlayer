export const DEMO_OPEN_ORDERS = [
  { id: 1, side: "sell", price: 3.6, amount: 5000 },
  { id: 2, side: "sell", price: 3.4, amount: 10000 },
  { id: 3, side: "sell", price: 3.2, amount: 15000 },
  { id: 4, side: "buy", price: 3.0, amount: 20000 },
  { id: 5, side: "buy", price: 2.8, amount: 10000 },
  { id: 6, side: "buy", price: 2.6, amount: 5000 },
];

export const DEMO_BALANCE = { SUI: 300000, USDT: 12999 };

export const DEMO_ORDER_BOOK = {
  bids: [
    [3.0, 20000],
    [2.8, 10000],
    [2.6, 5000],
  ],
  asks: [
    [3.2, 15000],
    [3.4, 10000],
    [3.6, 5000],
  ],
};

export function getDemoMarketSnapshot() {
  return {
    symbol: "SUI/USDT",
    dataSource: "binance",
    currentPrice: 3.22,
    volume: 1000000,
    orderBook: DEMO_ORDER_BOOK,
    openOrders: DEMO_OPEN_ORDERS,
    balance: DEMO_BALANCE,
  };
}

export async function fetchBinanceMarket(exchangeSymbol = "SUIUSDT") {
  const [depthRes, tickerRes] = await Promise.all([
    fetch(`https://api.binance.com/api/v3/depth?symbol=${exchangeSymbol}&limit=5`),
    fetch(`https://api.binance.com/api/v3/ticker/24hr?symbol=${exchangeSymbol}`),
  ]);

  if (!depthRes.ok || !tickerRes.ok) {
    throw new Error("Failed to fetch Binance market data");
  }

  const depth = await depthRes.json();
  const ticker = await tickerRes.json();

  return {
    orderBook: {
      bids: depth.bids.slice(0, 3).map(([price, qty]) => [parseFloat(price), parseFloat(qty)]),
      asks: depth.asks.slice(0, 3).map(([price, qty]) => [parseFloat(price), parseFloat(qty)]),
    },
    currentPrice: parseFloat(ticker.lastPrice),
    volume: parseFloat(ticker.volume),
  };
}
