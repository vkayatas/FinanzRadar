<template>
  <div class="bg-white dark:bg-gray-800 rounded-xl shadow p-4">
    <!-- Title -->
    <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Your Assets</h2>

    <!-- Allocation List -->
    <div class="space-y-4">
      <div 
        v-for="(asset, index) in allocationData" 
        :key="asset.name" 
        class="space-y-2"
      >
        <!-- Row 1: Icon Circle + Name + Value -->
        <div class="grid grid-cols-[auto_1fr] items-center gap-3">
          <div :class="getCircleColor(index)" class="w-12 h-12 rounded-full flex items-center justify-center">
            <component :is="getIcon(asset.name)" class="w-7 h-7 text-white" />
          </div>
          <div class="flex flex-col">
            <span class="font-medium text-gray-900 dark:text-white">{{ asset.name }}</span>
            <span class="text-sm text-gray-500 dark:text-gray-400">{{ formatCurrency(asset.value) }}</span>
          </div>
        </div>

        <!-- Row 2: Progress Bar + Percentage -->
        <div class="flex items-center gap-2">
          <div class="flex-1 bg-gray-200 dark:bg-gray-700 h-2 rounded">
            <div class="h-2 rounded" :class="getCircleColor(index)"  :style="{ width: asset.value + '%' }"></div>
          </div>
          <span class="text-sm text-gray-500 dark:text-gray-400">{{ asset.value }}%</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { defineProps } from 'vue'
import { CurrencyDollarIcon, DocumentTextIcon } from '@heroicons/vue/24/outline'

const props = defineProps({
  allocationData: { 
    type: Array, 
    default: () => [
      { value: 75, name: 'Stocks' }, 
      { value: 25, name: 'Cash' } 
    ] 
  }
})

// Icon mapper
const getIcon = (name) => {
  if (name.toLowerCase() === 'stocks') return DocumentTextIcon
  if (name.toLowerCase() === 'cash') return CurrencyDollarIcon
  return DocumentTextIcon
}

// Circle color mapper
const getCircleColor = (index) => {
  // First asset: indigo, second asset: teal or lighter indigo
  const colors = ['bg-indigo-500', 'bg-teal-500']
  return colors[index % colors.length]
}

// Format currency
const formatCurrency = (value) => {
  return new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(value * 1000)
}
</script>
