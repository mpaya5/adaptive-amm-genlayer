import Random from 'random';

class CCXTSimulator {
  /** 
   * To be able to use this simulator you will need to solve the problems with
   * the https-proxy-agent
   */
  constructor(symbol, exchange) {
    /**
     * Initializes the CCXTSimulator class with a trading pair symbol and exchange.
     *
     * @param {string} symbol - The trading pair symbol (e.g., 'BTC/USDT').
     * @param {string} exchange - The name of the exchange (e.g., 'binance').
     */
    const ccxt = window.ccxt;
    this.symbol = symbol;
    this.exchange = new ccxt[exchange]();
    this.random = Random;
  }

  // Retrieve market data functions
  async getOrderBook() {
    /**
     * Retrieves the order book data.
     */
    await this.exchange.loadMarkets();
    return await this.exchange.fetchOrderBook(this.symbol);
  }

  async getTicker() {
    /**
     * Retrieves the ticker of the asset.
     */
    return await this.exchange.fetchTicker(this.symbol);
  }

  async getCurrentPrice() {
    /**
     * Retrieves the current price of the asset.
     */
    const ticker = await this.getTicker();
    return ticker ? ticker.last : null;
  }

  async getVolume() {
    /**
     * Retrieves the 24-hour trading volume for the asset symbol.
     */
    const ticker = await this.getTicker();
    return ticker ? ticker.quoteVolume : this.random.float(500000, 1000000);
  }

  async getOpenOrders() {
    /**
     * Simulates creating open orders close to the current price.
     */
    const currentPrice = await this.getCurrentPrice();
    const numOrders = this.random.int(3, 7);
    const orders = [];
    for (let i = 0; i < numOrders; i++) {
      const side = i % 2 === 0 ? 'buy' : 'sell';
      const priceOffset = this.random.float(-0.005, 0.005);  // Slight offset from current price
      const price = currentPrice * (side === 'buy' ? (1 + priceOffset) : (1 - priceOffset));
      const amount = this.random.float(5000, 20000);
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
      [baseAsset]: this.random.float(200000, 500000),
      [quoteAsset]: this.random.float(100000, 300000)
    };
  }

  async closeConnection() {
    /**
     * Closes the exchange connection.
     */
    if (this.exchange && typeof this.exchange.close === 'function') {
      await this.exchange.close();
    }
  }
}

export default CCXTSimulator;
