<template>
    <div class="min-h-screen bg-gray-100 text-gray-900">
      <header class="bg-white shadow flex justify-between">
        <div class="max-w-7xl py-6 px-4 sm:px-6 lg:px-8">
          <h1 class="text-3xl font-bold text-gray-900">Adaptive AMM Dashboard</h1>
        </div>
      </header>
      <main class="mx-auto py-6 sm:px-6 lg:px-8">
        <div class="grid grid-cols-1 md:grid-cols-10 gap-8">
          <!-- Market Data -->
          <div class="bg-white shadow overflow-hidden sm:rounded-lg col-span-7">
            <div class="px-4 py-5 sm:px-6 flex justify-between items-center">
              <h2 class="text-lg leading-6 font-medium text-gray-900">{{ symbol }}</h2>
              <p><strong>Current Price:</strong> {{ currentPrice }}</p>
              <button
                @click="resolveOrders"
                :disabled="isLoading"
                class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded text-sm"
              >
                <span v-if="isLoading">Resolving...</span>
                <span v-else>Resolve Orders</span>
              </button>
            </div>
            <div v-if="decisionMessage" class="p-4 bg-yellow-200 text-yellow-800 rounded mb-4">
              {{ decisionMessage }}
            </div>
            <div class="border-t border-gray-200 p-4">
              <h2><strong>Account Info:</strong></h2>
              <hr><br>
              <p><strong>Balance:</strong> {{ balance.SUI }} SUI, {{ balance.USDT }} USDT</p>
  
              <h2 class="mt-6"><strong>Open Orders:</strong></h2>
              <table class="min-w-full divide-y divide-gray-200 mt-4">
                <thead class="bg-gray-50">
                  <tr>
                    <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Side
                    </th>
                    <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Price
                    </th>
                    <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Amount
                    </th>
                  </tr>
                </thead>
                <tbody class="bg-white divide-y divide-gray-200">
                  <tr v-for="order in openOrders" :key="order.id">
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {{ order.side.toUpperCase() }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {{ order.price }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {{ order.amount }}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </main>
    </div>
  </template>
  
  <script setup>
  import { ref, computed, onMounted } from "vue";
  import { account, createAccount, removeAccount } from "../services/genlayer";
  import AdaptiveAMM from "../logic/AdaptiveAMM";
  import Address from "./Address.vue";
  
  // State
  const contractAddress = import.meta.env.VITE_CONTRACT_ADDRESS;
  const adaptiveAMM = new AdaptiveAMM(contractAddress);
  const userAccount = ref(account);
  const userAddress = computed(() => userAccount.value?.address);
  
  const symbol = ref("SUI/USDT");
  const orderBook = ref({});
  const currentPrice = ref(0);
  const volume = ref(0);
  const openOrders = ref([]);
  const balance = ref({});
  const isLoading = ref(false);  
  const decisionMessage = ref("");
  
  // Methods
  const createUserAccount = async () => {
    userAccount.value = createAccount();
    adaptiveAMM.updateAccount(userAccount.value);  
  };
  
  const disconnectUserAccount = async () => {
    userAccount.value = null;
    removeAccount();
  };
  
  const loadMarketData = async () => {
    currentPrice.value = await adaptiveAMM.get_current_price();
    volume.value = await adaptiveAMM.get_volume();
    openOrders.value = await adaptiveAMM.get_open_orders();
    balance.value = await adaptiveAMM.get_balance();
  };
  
  // Resolve Method
  const resolveOrders = async () => {
    isLoading.value = true;  
    const result = await adaptiveAMM.resolve();

    if (result) {
      // Delete the cancelled orders
      openOrders.value = openOrders.value.filter(
        order => !result.cancel_orders.includes(order.id)
      );

      // Get last Id in the open orders
      let lastId = openOrders.value.length
        ? Math.max(...openOrders.value.map(order => order.id))
        : 0;

      // Add the new orders and set a new id
      result.new_orders.forEach(newOrder => {
        lastId += 1;
        openOrders.value.push({
          id: lastId, 
          ...newOrder
        });
      });

      // Show decision message for 16 seconds
      decisionMessage.value = result.reason_decision;
      setTimeout(() => {
        decisionMessage.value = ""; 
      }, 15000);
    }

    isLoading.value = false; 
  };
  

  onMounted(async () => {
    await createUserAccount();
    await loadMarketData();
  });
  </script>
  