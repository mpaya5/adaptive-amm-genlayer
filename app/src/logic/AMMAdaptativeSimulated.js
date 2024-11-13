import { createClient } from "genlayer-js";
import { simulator } from "genlayer-js/chains";
import CCXTSimulator  from "./CCXTSimulator";

class AMMAdaptiveSimulated {
  contractAddress;
  client;
  ccxtSimulator;
  symbol;
  exchange;
  open_orders;
  balance;
  
  constructor(contractAddress, account = null, symbol = "SUI/USDT", exchange="binance") {
    this.contractAddress = contractAddress;
    this.symbol = symbol;
    this.exchange = exchange;
    this.ccxtSimulator = new CCXTSimulator(symbol, exchange);
    const config = { chain: simulator, ...(account ? { account } : {}) };
    this.client = createClient(config);
  }

  updateAccount(account) {
    this.client = createClient({ chain: simulator, account });
  }

  get_order_book() {
    return this.ccxtSimulator.getOrderBook();
  }

  get_current_price() {
    return this.ccxtSimulator.getCurrentPrice();
  }

  get_volume() {
    return this.ccxtSimulator.getVolume();
  }

  get_open_orders() {
    this.open_orders = this.ccxtSimulator.getOpenOrders();
    return this.open_orders;
  }

  get_balance() {
    this.balance = this.ccxtSimulator.getBalance();
    return this.balance;
  }

  async resolve() {
    console.log([
      this.symbol, this.exchange, 0.5, 0.1, 0.01, 0.02, 10000.0, 1000.0, this.get_order_book(),
      this.get_current_price(), this.get_volume(), this.open_orders, this.balance
    ]);
    const txHash = await this.client.writeContract({
        address: this.contractAddress,
        functionName: "resolve",
        args: [
            this.symbol, this.exchange, 0.5, 0.1, 0.01, 0.02, 10000.0, 1000.0, this.get_order_book(),
            this.get_current_price(), this.get_volume(), this.open_orders, this.balance
        ]
    });

    const receipt = await this.client.waitForTransactionReceipt({
        hash: txHash,
        status: "FINALIZED",
        interval: 10000,
        retries: 20,
    });
    console.log(receipt)

    const result = await this.client.readContract({
        address: this.contractAddress,
        functionName: "get_resolve_response",
        args: []
    });
    console.log(result)
    return result;

  }
}

export default AMMAdaptiveSimulated;
