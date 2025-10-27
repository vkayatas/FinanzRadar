<template>
  <TransitionRoot as="template" :show="modelValue">
    <Dialog as="div" class="relative z-50" @close="close">
      <!-- Overlay -->
      <div class="fixed inset-0 bg-black/20 backdrop-blur-sm pointer-events-auto"></div>

      <!-- Centered modal -->
      <div class="fixed inset-0 flex items-center justify-center pointer-events-none">
        <TransitionChild
          enter="transition ease-out duration-150"
          enter-from="opacity-0 scale-95"
          enter-to="opacity-100 scale-100"
          leave="transition ease-in duration-100"
          leave-from="opacity-100 scale-100"
          leave-to="opacity-0 scale-95"
        >
          <DialogPanel
            class="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 w-[50vw] max-h-[90vh] overflow-visible pointer-events-auto"
            @keydown.enter.prevent="store.selectedStock && addStock()"
            tabindex="0"
          >
            <DialogTitle class="text-lg font-semibold text-gray-900 dark:text-gray-100 pb-2">
              Add Stock
            </DialogTitle>

            <div class="mt-4">
              <!-- Stock autocomplete uses orchestrator store -->
              <StockSearchAutocomplete />
            </div>

            <div class="mt-6 flex justify-between pt-6">
              <button
                class="px-4 py-2 rounded bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600"
                @click="close"
              >
                Cancel
              </button>
              <button
                class="px-4 py-2 rounded bg-indigo-500 text-white hover:bg-indigo-600"
                :disabled="!store.selectedStock"
                @click="addStock"
              >
                Add Stock
              </button>
            </div>
          </DialogPanel>
        </TransitionChild>
      </div>
    </Dialog>
  </TransitionRoot>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue'
import { Dialog, DialogPanel, DialogTitle, TransitionRoot, TransitionChild } from '@headlessui/vue'
import StockSearchAutocomplete from '@/components/subcomponents/StockSearchAutocomplete.vue'
import { useStockOrchestrator } from '@/stores/stockOrchestrator'
import { formatCurrency } from '@/api/utils/mathUtils.js'

// Props & emits
const props = defineProps({
  modelValue: Boolean,
  activeWatchlist: Object
})
const emit = defineEmits(['update:modelValue', 'add'])

// Use orchestrator store
const store = useStockOrchestrator()

// Close dialog
function close() {
  store.selectedStock = null
  emit('update:modelValue', false)
}

// Add stock to watchlist
function addStock() {
  const stock = store.selectedStock
  if (stock && props.activeWatchlist) {
    emit('add', {
      stock: {
        ticker: stock.symbol,
        company: stock.name,
        marketCap: stock.marketCap ? formatCurrency(stock.marketCap) : '$0'
      }
    })
  }
  close()
}
</script>
