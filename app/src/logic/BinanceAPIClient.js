import random from 'random';

class BinanceSimulator {
    /**
     * 
     * If you want to iteract with that simulator you will need to take care of the
     * cors policy.
     */
  constructor(symbol) {
    /**
     * Initializes the BinanceSimulator class with a trading pair symbol.
     *
     * @param {string} symbol - The trading pair symbol (e.g., 'BTCUSDT').
     */
    this.symbol = symbol;
    this.apiUrl = 'https://api.binance.com/api/v3';
  }

  async getOrderBook() {
    /**
     * Retrieves the order book data.
     */
    const response = await fetch(`${this.apiUrl}/depth?symbol=${this.symbol}`);
    const data = await response.json();
    return data;
  }

  async getTicker() {
    /**
     * Retrieves the ticker of the asset.
     */
    const response = await fetch(`${this.apiUrl}/ticker/24hr?symbol=${this.symbol}`);
    const data = await response.json();
    return data;
  }

  async getCurrentPrice() {
    /**
     * Retrieves the current price of the asset.
     */
    const ticker = await this.getTicker();
    return ticker ? parseFloat(ticker.lastPrice) : null;
  }

  async getVolume() {
    /**
     * Retrieves the 24-hour trading volume for the asset symbol.
     */
    const ticker = await this.getTicker();
    return ticker ? parseFloat(ticker.volume) : random.float(500000, 1000000);
  }

  async getOpenOrders() {
    /**
     * Simulates creating open orders close to the current price.
     */
    const currentPrice = await this.getCurrentPrice();
    const numOrders = random.int(3, 7);
    const orders = [];
    for (let i = 0; i < numOrders; i++) {
      const side = i % 2 === 0 ? 'buy' : 'sell';
      const priceOffset = random.float(-0.005, 0.005);  // Slight offset from current price
      const price = currentPrice * (side === 'buy' ? (1 + priceOffset) : (1 - priceOffset));
      const amount = random.float(5000, 20000);
      orders.push({
        id: i + 1,
        side: side,
        price: parseFloat(price.toFixed(4)),
        amount: parseFloat(amount.toFixed(2))
      });
    }
    return orders;
  }
  
  getBalance() {
    /**
     * Simulates a balance for the symbol and its quote asset.
     */
    const [baseAsset, quoteAsset] = this.symbol.split('/');
    return {
      [baseAsset]: random.float(200000, 500000),
      [quoteAsset]: random.float(100000, 300000)
    };
  }
}

export default BinanceSimulator;
