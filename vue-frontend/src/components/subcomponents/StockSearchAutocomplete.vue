<template>
  <Combobox v-model="store.selectedStock">
    <div class="relative">
      <div class=" w-full cursor-default overflow-hidden rounded-2xl 
                  bg-white/90 dark:bg-gray-800/90 backdrop-blur 
                  shadow-lg ring-1 ring-gray-200 dark:ring-gray-700 
                  focus-within:ring-2 focus-within:ring-indigo-500">
        <ComboboxInput
          class="w-full border-none py-3 pl-4 pr-10 text-gray-900 dark:text-white 
                 bg-transparent placeholder-gray-400 focus:ring-0 sm:text-sm"
          :placeholder="$t('stocks.messages.autocompletePlaceholder')"
          @input="query = $event.target.value"
          :display-value="stock => stock ? `${stock.symbol} - ${stock.name}` : ''"
          autocomplete="off"
        />
        <ComboboxButton class="absolute inset-y-0 right-0 flex items-center pr-3">
          <ChevronUpDownIcon class="h-5 w-5 text-gray-400" aria-hidden="true" />
        </ComboboxButton>
      </div>
<ComboboxOptions
  class="absolute z-50 mt-2 max-h-72 w-full overflow-auto rounded-2xl bg-white dark:bg-gray-800 py-2 shadow-2xl ring-1 ring-black/5 focus:outline-none sm:text-sm"
>

        <div v-if="filteredStocks.length === 0 && query !== ''"
             class="px-4 py-2 text-gray-500 dark:text-gray-400 italic">
          {{ $t('stocks.messages.noResults') }}
        </div>

        <ComboboxOption
          v-for="stock in filteredStocks"
          :key="stock.symbol"
          :value="stock"
          v-slot="{ active, selected }"
          as="template"
        >
          <li class="relative cursor-pointer select-none px-4 py-3 transition-colors rounded-lg mx-1"
              :class="[active ? 'bg-indigo-50 dark:bg-indigo-600/30 ring-1 ring-indigo-500' : '',
                       selected ? 'bg-indigo-100 dark:bg-indigo-700/40' : '']">
            <div class="flex justify-between items-center">
              <span :class="['font-medium truncate', selected ? 'text-indigo-600 dark:text-indigo-400' : 'text-gray-900 dark:text-gray-100']">
                {{ stock.symbol }} - {{ stock.name }}
              </span>
            </div>
            <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">{{ stock.sector }}</p>
          </li>
        </ComboboxOption>
      </ComboboxOptions>
    </div>
  </Combobox>
</template>

<script setup>
import Fuse from 'fuse.js' //helper function for keyword search
import { ref, computed } from 'vue'
import { ChevronUpDownIcon } from '@heroicons/vue/20/solid'
import { Combobox, ComboboxInput, ComboboxButton, ComboboxOptions, ComboboxOption } from '@headlessui/vue'
import tickerSearch from '@/assets/tickerSearch.json'
import tickerSearchPopular from '@/assets/tickerSearchPopular.json'
import { useStockOrchestrator } from '@/stores/stockOrchestrator'

// Params
const autocompleteMaxResults = 20
const stocksList = tickerSearch
const popularStocks = tickerSearchPopular

// Init data from pinia
const store = useStockOrchestrator()

// Autocomplete input variables and fuse-search
const query = ref('')
const fuse = new Fuse(stocksList, { keys: ['symbol', 'name'], threshold: 0.3 })

// Returns stock hit list using fuse
const filteredStocks = computed(() => {
  if (!query.value) {
    return popularStocks
      .slice()
      .sort((a, b) => b.marketCap - a.marketCap)
      .slice(0, autocompleteMaxResults)
  }
  return fuse
    .search(query.value)
    .slice(0, autocompleteMaxResults)
    .map(r => r.item)
})
</script>
