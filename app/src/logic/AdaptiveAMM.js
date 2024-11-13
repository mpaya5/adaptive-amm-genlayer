import { createClient } from "genlayer-js";
import { simulator } from "genlayer-js/chains";

class AdaptiveAMM {
  contractAddress;
  client;

  constructor(contractAddress, account = null) {
    this.contractAddress = contractAddress;
    const config = { chain: simulator, ...(account ? { account } : {}) };
    this.client = createClient(config);
  }

  updateAccount(account) {
    this.client = createClient({ chain: simulator, account });
  }

  async get_order_book() {
    const result = await this.client.readContract({
        address: this.contractAddress,
        functionName: "get_order_book",
        args: []
    });
    return result;
  }

  async get_current_price() {
    const result = await this.client.readContract({
        address: this.contractAddress,
        functionName: "get_current_price",
        args: []
    });
    return result;
  }

  async get_volume() {
    const result = await this.client.readContract({
        address: this.contractAddress,
        functionName: "get_volume",
        args: []
    });
    return result;
  }

  async get_open_orders() {
    const result = await this.client.readContract({
        address: this.contractAddress,
        functionName: "get_open_orders",
        args: []
    });
    return result;
  }

  async get_balance() {
    const result = await this.client.readContract({
        address: this.contractAddress,
        functionName: "get_balance",
        args: []
    });
    return result;
  }

  async resolve() {
    const txHash = await this.client.writeContract({
        address: this.contractAddress,
        functionName: "resolve",
        args: []
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

export default AdaptiveAMM;
