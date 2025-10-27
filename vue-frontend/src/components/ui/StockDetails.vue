<template>
  <div
    v-if="store.selectedStock"
    class="p-4 bg-white dark:bg-gray-800 rounded-2xl shadow-lg flex flex-col items-center text-center"
  >
    <!-- Header with logo and name -->
    <div class="flex items-center space-x-4 mb-4">
      <img
        :src="`https://storage.googleapis.com/iex/api/logos/${store.selectedStock.symbol}.png`"
        :alt="`${store.selectedStock.name} logo`"
        class="w-16 sm:w-22 h-16 sm:h-22 rounded-full shadow-lg"
      />
      <h2 class="text-xl sm:text-3xl font-bold font-sans tracking-tight text-gray-900 dark:text-white">
        {{ store.selectedStock.name }} ({{ store.selectedStock.symbol }})
      </h2>
    </div>

    <!-- Price + change tag -->
    <div class="flex items-center justify-center space-x-3 mb-2">
      <span class="text-2xl sm:text-3xl font-semibold text-gray-900 dark:text-white">
        {{ formatCurrency(store.stockInfo.details.currentPrice.toFixed(2), "$") }}
      </span>
      <PriceChangeTag :value="store.stockInfo.details.relChange" class="translate-y-0.5"/>
    </div>

    <!-- Last updated -->
    <p class="text-sm sm:text-base text-gray-500 dark:text-gray-400 mb-6">
        {{ $t('stocks.labels.lastUpdated') }}: {{ formatDate(store.stockInfo.details.lastUpdated) }}
      <span v-if="store.stockInfo.details.isLive" class="ml-2 text-xs px-2 py-1 rounded bg-blue-100 text-blue-700 dark:bg-blue-800 dark:text-blue-100">
        LIVE
      </span>
    </p>

    <!-- Performance row -->
    <div class="flex flex-wrap justify-center gap-4 mb-4">
      <PriceChangeTag
        v-for="(perf, label) in store.stockInfo.details.performance"
        :key="label"
        :value="perf.relStockPriceChange"
        :label="label"
      />
    </div>

    <!-- Extra info: single row -->
    <div class="flex flex-wrap justify-center gap-2 md:gap-4 text-base text-gray-700 dark:text-gray-300">
      <div class="flex space-x-1 items-center">
        <span class="font-semibold text-sm sm:text-base">{{ $t('stocks.labels.industry') }}:</span>
        <span class="text-sm sm:text-base">{{ store.stockInfo.details.industry }}</span>
      </div>
      <div class="flex space-x-1 items-center text-sm sm:text-base">
        <span class="font-semibold">{{ $t('stocks.labels.sector') }}:</span>
        <span class="text-sm sm:text-base">{{ store.stockInfo.details.sector }}</span>
      </div>
      <div class="flex space-x-1 items-center text-sm sm:text-base">
        <span class="font-semibold">{{ $t('stocks.labels.country') }}:</span>
        <span class="text-sm sm:text-base">{{ store.stockInfo.details.country }}</span>
      </div>
    </div>

  </div>
</template>

<script setup>
import {formatDate} from '@/api/utils/dateUtils.js'
import {formatCurrency} from '@/api/utils/mathUtils.js'
import { useStockOrchestrator } from '@/stores/stockOrchestrator'
import PriceChangeTag from '@/components/subcomponents/PriceChangeTag.vue'

// init pinia store
const store = useStockOrchestrator()
</script>
