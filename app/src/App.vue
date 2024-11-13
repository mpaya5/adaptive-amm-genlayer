<template>
  <Suspense>
    <template #default>
      <AdaptiveAMMScreen />
      <!-- <AMMAdaptativeSimulatedScreen/> -->
    </template>
    <template #fallback>
      <div class="flex items-center justify-center h-screen">
        <div class="spinner">Loading...</div>
      </div>
    </template>
  </Suspense>
</template>

<script setup>
import AdaptiveAMMScreen from "./components/AdaptiveAMMScreen.vue";
// import AMMAdaptativeSimulatedScreen from "./components/AMMAdaptativeSimulatedScreen.vue";
</script>
