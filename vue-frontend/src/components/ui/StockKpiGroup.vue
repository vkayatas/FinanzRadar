<template>
  <div v-if="store.selectedStock" class="bg-gray-50 dark:bg-gray-900 p-2 sm:p-4 rounded-2xl shadow-lg">
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-6">
      <KpiGroup
        v-for="group in store.stockInfo.kpis"
        :key="group.title"
        :title="group.title"
        :kpis="group.kpis"
        class="text-xs sm:md:text-sm md:text-base"
      />
    </div>
  </div>
</template>

<script setup>
import KpiGroup from '@/components/subcomponents/KpiGroup.vue'
import { useStockOrchestrator } from '@/stores/stockOrchestrator'

// Init store and fetch data
const store = useStockOrchestrator()
</script>
