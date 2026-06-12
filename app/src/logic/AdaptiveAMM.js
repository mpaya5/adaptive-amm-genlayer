import { createClient } from "genlayer-js";
import { localnet } from "genlayer-js/chains";
import { ExecutionResult, TransactionStatus } from "genlayer-js/types";
import {
  fetchBinanceMarket,
  getDemoMarketSnapshot,
} from "./demoMarketData.js";

const READ_OPTS = { stateStatus: "accepted" };
const DEMO_MODE = import.meta.env.VITE_DEMO_MODE === "true";

class AdaptiveAMM {
  contractAddress;
  client;
  account;
  demoState;

  constructor(contractAddress, account = null) {
    this.contractAddress = contractAddress;
    this.account = account;
    this.demoState = getDemoMarketSnapshot();
    this.client = createClient({
      chain: localnet,
      ...(account ? { account } : {}),
    });
  }

  updateAccount(account) {
    this.account = account;
    this.client = createClient({ chain: localnet, account });
  }

  async read(functionName, args = []) {
    if (DEMO_MODE) {
      const map = {
        get_symbol: () => this.demoState.symbol,
        get_data_source: () => this.demoState.dataSource,
        get_current_price: () => this.demoState.currentPrice,
        get_volume: () => this.demoState.volume,
        get_order_book: () => this.demoState.orderBook,
        get_open_orders: () => this.demoState.openOrders,
        get_balance: () => this.demoState.balance,
        get_resolve_response: () => ({
          cancel_orders: [],
          new_orders: [],
          reason_decision:
            "Demo mode: connect a deployed contract to run live resolve().",
        }),
      };
      if (map[functionName]) return map[functionName]();
      throw new Error(`Unknown read method: ${functionName}`);
    }

    return this.client.readContract({
      address: this.contractAddress,
      functionName,
      args,
      ...READ_OPTS,
    });
  }

  async write(functionName, args = []) {
    if (DEMO_MODE) {
      if (functionName === "refresh_market_data") {
        const live = await fetchBinanceMarket("SUIUSDT");
        this.demoState = { ...this.demoState, ...live };
        return { txExecutionResultName: ExecutionResult.FINISHED_WITH_RETURN };
      }
      if (functionName === "resolve") {
        await this.write("refresh_market_data");
        this.demoState.reasonDecision =
          "Demo mode preview — deploy the contract for on-chain LLM resolve.";
        return { txExecutionResultName: ExecutionResult.FINISHED_WITH_RETURN };
      }
      return { txExecutionResultName: ExecutionResult.FINISHED_WITH_RETURN };
    }

    const txHash = await this.client.writeContract({
      account: this.account,
      address: this.contractAddress,
      functionName,
      args,
      value: 0n,
    });

    const receipt = await this.client.waitForTransactionReceipt({
      hash: txHash,
      status: TransactionStatus.FINALIZED,
      interval: 10000,
      retries: 20,
    });

    if (receipt.txExecutionResultName !== ExecutionResult.FINISHED_WITH_RETURN) {
      throw new Error(`${functionName}() failed: ${receipt.txExecutionResultName ?? "unknown"}`);
    }

    return receipt;
  }

  async get_symbol() {
    return this.read("get_symbol");
  }

  async get_data_source() {
    return this.read("get_data_source");
  }

  async get_order_book() {
    return this.read("get_order_book");
  }

  async get_current_price() {
    return this.read("get_current_price");
  }

  async get_volume() {
    return this.read("get_volume");
  }

  async get_open_orders() {
    return this.read("get_open_orders");
  }

  async get_balance() {
    return this.read("get_balance");
  }

  async get_resolve_response() {
    return this.read("get_resolve_response");
  }

  async refreshMarketData() {
    await this.write("refresh_market_data");
  }

  async loadMarketData() {
    const [symbol, dataSource, currentPrice, volume, orderBook, openOrders, balance] =
      await Promise.all([
        this.get_symbol(),
        this.get_data_source(),
        this.get_current_price(),
        this.get_volume(),
        this.get_order_book(),
        this.get_open_orders(),
        this.get_balance(),
      ]);
    return { symbol, dataSource, currentPrice, volume, orderBook, openOrders, balance };
  }

  async resolve() {
    await this.write("resolve");
    return this.get_resolve_response();
  }
}

export default AdaptiveAMM;
