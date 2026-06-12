<template>
  <div class="min-h-screen bg-slate-100 text-slate-900 flex flex-col">
    <!-- Header -->
    <header class="bg-white border-b border-slate-200">
      <div class="max-w-6xl mx-auto px-4 sm:px-6 py-4 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="w-9 h-9 rounded-full bg-blue-500 flex items-center justify-center">
            <Droplets class="w-5 h-5 text-white" />
          </div>
          <h1 class="text-xl font-bold text-slate-900">Adaptive AMM Dashboard</h1>
        </div>
        <div class="flex items-center gap-3">
          <span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-blue-50 text-blue-600 text-sm font-medium border border-blue-100">
            <BarChart3 class="w-3.5 h-3.5" />
            Basic AMM Mode
          </span>
          <div class="relative" ref="walletMenuRef">
            <button
              @click="walletMenuOpen = !walletMenuOpen"
              class="inline-flex items-center gap-2 px-3 py-2 rounded-lg border border-slate-200 bg-white hover:bg-slate-50 text-sm font-medium text-slate-700 transition-colors"
            >
              <Wallet class="w-4 h-4 text-blue-500" />
              <Address v-if="userAddress" :address="userAddress" :max-length="13" />
              <span v-else class="text-slate-400">Connect</span>
              <ChevronDown class="w-4 h-4 text-slate-400" />
            </button>
            <div
              v-if="walletMenuOpen"
              class="absolute right-0 mt-2 w-56 rounded-lg bg-white border border-slate-200 shadow-lg z-10 py-1"
            >
              <button
                @click="handleDisconnect"
                class="w-full text-left px-4 py-2 text-sm text-slate-700 hover:bg-slate-50"
              >
                Disconnect wallet
              </button>
              <button
                @click="handleReconnect"
                class="w-full text-left px-4 py-2 text-sm text-slate-700 hover:bg-slate-50"
              >
                New account
              </button>
            </div>
          </div>
        </div>
      </div>
    </header>

    <main class="flex-1 max-w-6xl mx-auto w-full px-4 sm:px-6 py-6 space-y-5">
      <!-- Pair + Price + Action -->
      <div class="bg-white rounded-xl border border-slate-200 shadow-sm p-5 sm:p-6">
        <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-5">
          <div class="flex items-center gap-4">
            <div class="flex items-center -space-x-2">
              <div class="w-11 h-11 rounded-full bg-blue-500 border-2 border-white flex items-center justify-center z-10">
                <Droplets class="w-5 h-5 text-white" />
              </div>
              <div class="w-11 h-11 rounded-full bg-emerald-500 border-2 border-white flex items-center justify-center text-white font-bold text-sm">
                T
              </div>
            </div>
            <div>
              <h2 class="text-2xl font-bold text-slate-900">{{ symbol }}</h2>
              <p class="text-sm text-slate-500">
                Sui Network · Live feed via GenLayer
                <span v-if="dataSource" class="text-blue-600 font-medium"> · {{ dataSource }}</span>
              </p>
            </div>
          </div>

          <div class="text-center sm:text-left">
            <p class="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">Current Price</p>
            <p class="text-4xl font-bold text-slate-900 leading-none">{{ formatPrice(currentPrice) }}</p>
            <p class="text-sm text-slate-500 mt-1">USDT per SUI</p>
          </div>

          <button
            @click="resolveOrders"
            :disabled="isLoading"
            class="inline-flex items-center justify-center gap-2 px-6 py-3 rounded-lg bg-blue-500 hover:bg-blue-600 disabled:bg-blue-300 text-white font-semibold text-sm transition-colors shadow-sm"
          >
            <RefreshCw :class="['w-4 h-4', isLoading && 'animate-spin']" />
            <span>{{ isLoading ? "Resolving..." : "Resolve Orders" }}</span>
          </button>
        </div>
      </div>

      <!-- Static info banner (matches dashboard screenshot) -->
      <div class="rounded-xl bg-amber-50 border border-amber-200 p-4 flex gap-3">
        <Lightbulb class="w-5 h-5 text-amber-500 shrink-0 mt-0.5" />
        <div>
          <p class="font-semibold text-amber-900 text-sm">Market-Making in Basic AMM Mode</p>
          <p class="text-sm text-amber-800 mt-1 leading-relaxed">
            The contract fetches a live order book on-chain via <code class="text-xs bg-amber-100 px-1 rounded">gl.nondet.web.get</code>
            (Binance public API). Click "Resolve Orders" to refresh market data, run LLM market-making consensus, and update your orders.
          </p>
        </div>
      </div>

      <div
        v-if="marketError"
        class="rounded-xl bg-red-50 border border-red-200 p-4 text-sm text-red-800"
      >
        {{ marketError }}
      </div>

      <!-- AI decision (shown after resolve) -->
      <div
        v-if="aiDecision"
        class="rounded-xl bg-blue-50 border border-blue-200 p-4 text-sm text-blue-900 leading-relaxed"
      >
        <p class="font-semibold text-blue-800 mb-1">AI Market-Making Decision</p>
        {{ aiDecision }}
      </div>

      <!-- Live Order Book -->
      <div class="bg-white rounded-xl border border-slate-200 shadow-sm p-5">
        <div class="flex items-center justify-between mb-4">
          <div class="flex items-center gap-2">
            <BarChart3 class="w-5 h-5 text-blue-500" />
            <h3 class="font-semibold text-slate-900">Live Order Book</h3>
          </div>
          <span class="text-xs text-slate-400">24h vol: {{ formatNumber(volume) }} USDT</span>
        </div>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
          <div>
            <p class="text-xs font-semibold text-emerald-600 uppercase mb-2">Bids</p>
            <div
              v-for="(bid, i) in orderBook.bids"
              :key="'bid-' + i"
              class="flex justify-between py-1 border-b border-slate-50"
            >
              <span class="text-emerald-700 font-medium">{{ formatPrice(bid[0]) }}</span>
              <span class="text-slate-600">{{ formatNumber(bid[1]) }}</span>
            </div>
          </div>
          <div>
            <p class="text-xs font-semibold text-red-500 uppercase mb-2">Asks</p>
            <div
              v-for="(ask, i) in orderBook.asks"
              :key="'ask-' + i"
              class="flex justify-between py-1 border-b border-slate-50"
            >
              <span class="text-red-600 font-medium">{{ formatPrice(ask[0]) }}</span>
              <span class="text-slate-600">{{ formatNumber(ask[1]) }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Account + Orders -->
      <div class="grid grid-cols-1 lg:grid-cols-5 gap-5">
        <!-- Account Info -->
        <div class="lg:col-span-2 bg-white rounded-xl border border-slate-200 shadow-sm p-5">
          <div class="flex items-center gap-2 mb-4">
            <User class="w-5 h-5 text-blue-500" />
            <h3 class="font-semibold text-slate-900">Account Info</h3>
          </div>
          <p class="text-sm font-medium text-slate-500 mb-3">Balance</p>
          <div class="space-y-3">
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-2">
                <div class="w-7 h-7 rounded-full bg-blue-500 flex items-center justify-center">
                  <Droplets class="w-3.5 h-3.5 text-white" />
                </div>
                <span class="font-medium text-slate-700">SUI</span>
              </div>
              <span class="font-bold text-slate-900">{{ formatNumber(balance.SUI) }}</span>
            </div>
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-2">
                <div class="w-7 h-7 rounded-full bg-emerald-500 flex items-center justify-center text-white text-xs font-bold">
                  T
                </div>
                <span class="font-medium text-slate-700">USDT</span>
              </div>
              <span class="font-bold text-slate-900">{{ formatNumber(balance.USDT) }}</span>
            </div>
          </div>
        </div>

        <!-- Open Orders -->
        <div class="lg:col-span-3 bg-white rounded-xl border border-slate-200 shadow-sm p-5">
          <div class="flex items-center gap-2 mb-4">
            <ClipboardList class="w-5 h-5 text-blue-500" />
            <h3 class="font-semibold text-slate-900">Open Orders</h3>
          </div>
          <table class="w-full text-sm">
            <thead>
              <tr class="text-left text-slate-400 text-xs uppercase tracking-wider border-b border-slate-100">
                <th class="pb-3 font-semibold">Side</th>
                <th class="pb-3 font-semibold">Price (USDT)</th>
                <th class="pb-3 font-semibold text-right">Amount (SUI)</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="order in sellOrders"
                :key="'sell-' + order.id"
                class="border-b border-slate-50"
              >
                <td class="py-3 font-semibold text-red-500">Sell</td>
                <td class="py-3 text-slate-800">{{ formatPrice(order.price) }}</td>
                <td class="py-3 text-right text-slate-800">{{ formatNumber(order.amount) }}</td>
              </tr>
              <tr v-if="sellOrders.length && buyOrders.length">
                <td colspan="3" class="py-1">
                  <div class="border-t border-dashed border-slate-200"></div>
                </td>
              </tr>
              <tr
                v-for="order in buyOrders"
                :key="'buy-' + order.id"
                class="border-b border-slate-50 last:border-0"
              >
                <td class="py-3 font-semibold text-emerald-600">Buy</td>
                <td class="py-3 text-slate-800">{{ formatPrice(order.price) }}</td>
                <td class="py-3 text-right text-slate-800">{{ formatNumber(order.amount) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </main>

    <footer class="py-4 text-center text-xs text-slate-400">
      Adaptive AMM Protocol &copy; 2024
    </footer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from "vue";
import {
  BarChart3,
  ChevronDown,
  ClipboardList,
  Droplets,
  Lightbulb,
  RefreshCw,
  User,
  Wallet,
} from "lucide-vue-next";
import { account, createAccount, removeAccount } from "../services/genlayer";
import AdaptiveAMM from "../logic/AdaptiveAMM";
import Address from "./Address.vue";

const contractAddress = import.meta.env.VITE_CONTRACT_ADDRESS;
const adaptiveAMM = new AdaptiveAMM(contractAddress);

const userAccount = ref(account);
const userAddress = computed(() => userAccount.value?.address);
const walletMenuOpen = ref(false);
const walletMenuRef = ref(null);

const symbol = ref("SUI/USDT");
const dataSource = ref("");
const currentPrice = ref(0);
const volume = ref(0);
const orderBook = ref({ bids: [], asks: [] });
const openOrders = ref([]);
const balance = ref({ SUI: 0, USDT: 0 });
const isLoading = ref(false);
const aiDecision = ref("");
const marketError = ref("");

const sellOrders = computed(() =>
  openOrders.value
    .filter((o) => o.side === "sell")
    .sort((a, b) => b.price - a.price)
);

const buyOrders = computed(() =>
  openOrders.value
    .filter((o) => o.side === "buy")
    .sort((a, b) => b.price - a.price)
);

const formatNumber = (value) => {
  if (value == null || value === "") return "—";
  return Number(value).toLocaleString("en-US");
};

const formatPrice = (value) => {
  if (value == null || value === "") return "—";
  return Number(value).toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
};

const createUserAccount = () => {
  userAccount.value = createAccount();
  adaptiveAMM.updateAccount(userAccount.value);
};

const handleDisconnect = () => {
  removeAccount();
  userAccount.value = null;
  walletMenuOpen.value = false;
};

const handleReconnect = () => {
  createUserAccount();
  walletMenuOpen.value = false;
};

const loadMarketData = async () => {
  const data = await adaptiveAMM.loadMarketData();
  symbol.value = data.symbol;
  dataSource.value = data.dataSource;
  currentPrice.value = data.currentPrice;
  volume.value = data.volume;
  orderBook.value = data.orderBook ?? { bids: [], asks: [] };
  openOrders.value = data.openOrders;
  balance.value = data.balance;
};

const refreshLiveMarket = async () => {
  marketError.value = "";
  try {
    await adaptiveAMM.refreshMarketData();
    await loadMarketData();
  } catch (err) {
    marketError.value = err.message;
  }
};

const resolveOrders = async () => {
  isLoading.value = true;
  aiDecision.value = "";

  try {
    const result = await adaptiveAMM.resolve();
    await loadMarketData();

    if (result?.reason_decision) {
      aiDecision.value = result.reason_decision;
      setTimeout(() => { aiDecision.value = ""; }, 20000);
    }
  } catch (err) {
    aiDecision.value = `Error: ${err.message}`;
  } finally {
    isLoading.value = false;
  }
};

const onClickOutside = (e) => {
  if (walletMenuRef.value && !walletMenuRef.value.contains(e.target)) {
    walletMenuOpen.value = false;
  }
};

onMounted(async () => {
  if (!userAccount.value) createUserAccount();
  else adaptiveAMM.updateAccount(userAccount.value);
  await loadMarketData();
  await refreshLiveMarket();
  document.addEventListener("click", onClickOutside);
});

onUnmounted(() => {
  document.removeEventListener("click", onClickOutside);
});
</script>
