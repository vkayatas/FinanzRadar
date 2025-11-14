<template>
  <Combobox v-model="store.selectedStock">
    <div class="relative">
      <!-- Input box -->
      <div class="w-full cursor-default overflow-hidden rounded-2xl 
                  bg-white/90 dark:bg-gray-800/90 backdrop-blur 
                  shadow-lg ring-1 ring-gray-200 dark:ring-gray-700 
                  focus-within:ring-2 focus-within:ring-indigo-500">
        <ComboboxInput
          class="w-full border-none py-3 pl-4 pr-10 text-gray-900 dark:text-white 
                 bg-transparent placeholder-gray-400 focus:ring-0 sm:text-sm"
          :placeholder="$t('stocks.messages.autocompletePlaceholder')"
          @input="onInput"
          :display-value="stock => stock ? `${stock.symbol} - ${stock.name}` : ''"
          autocomplete="off"
        />
        <ComboboxButton class="absolute inset-y-0 right-0 flex items-center pr-3">
          <ChevronUpDownIcon class="h-5 w-5 text-gray-400" aria-hidden="true" />
        </ComboboxButton>
      </div>

      <!-- Options dropdown -->
      <ComboboxOptions
        v-if="stocksReady"
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
            <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">{{ stock.sector }} • {{ formatCurrency(stock.marketCap) }}</p>
          </li>
        </ComboboxOption>
      </ComboboxOptions>
    </div>
  </Combobox>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ChevronUpDownIcon } from '@heroicons/vue/20/solid'
import { Combobox, ComboboxInput, ComboboxButton, ComboboxOptions, ComboboxOption } from '@headlessui/vue'
import Fuse from 'fuse.js'
import debounce from 'lodash/debounce'
import tickerSearchPopular from '@/assets/tickerSearchPopular.json'
import { useStockOrchestrator } from '@/stores/stockOrchestrator'
import { formatCurrency } from '@/api/utils/mathUtils.js'

// Params
const autocompleteMaxResults = 20
const maxPrefixLength = 3

// Pinia store
const store = useStockOrchestrator()

// Reactive input
const query = ref('')
const debouncedQuery = ref('')

// Debounce input
const updateDebouncedQuery = debounce(val => {
  debouncedQuery.value = val
}, 250)

const onInput = (event) => {
  query.value = event.target.value
  updateDebouncedQuery(event.target.value)
}

// Prefix map and full stock data
const prefixMap = ref(new Map())   // prefix -> [symbols]
const tickerData = ref({})         // symbol -> stock object
const fuseReady = ref(false)
const stocksReady = ref(false)

// Load prefix map and ticker data
onMounted(async () => {
  const prefixModule = await import('@/assets/tickerSearchPrefixMap.json')
  prefixMap.value = new Map(Object.entries(prefixModule.default))

  const tickerModule = await import('@/assets/tickerSearchUS.json')
  tickerData.value = tickerModule.default

  fuseReady.value = true
  stocksReady.value = true
})

// Optimized filtered stocks
const filteredStocks = computed(() => {
  const q = debouncedQuery.value.trim().toLowerCase()

  if (!q) {
    return tickerSearchPopular
      .slice()
      .sort((a, b) => b.marketCap - a.marketCap)
      .slice(0, autocompleteMaxResults)
  }

  const prefixKey = q.slice(0, maxPrefixLength)
  const candidateSymbols = prefixMap.value.get(prefixKey) || []

  if (!candidateSymbols.length) return []

  // Map symbols to full stock objects
  let candidates = candidateSymbols
    .map(sym => tickerData.value[sym])
    .filter(Boolean)

  // Optional fuzzy search within candidates
  if (candidates.length > 0 && q.length > 1) {
    const fuse = new Fuse(candidates, { keys: ['symbol', 'name'], threshold: 0.3, distance: 30 })
    candidates = fuse.search(q).map(r => r.item)
  }

  return candidates
    .sort((a, b) => b.marketCap - a.marketCap)
    .slice(0, autocompleteMaxResults)
})
</script>
