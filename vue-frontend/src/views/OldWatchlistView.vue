<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 p-4 sm:p-6 lg:p-8">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-6">
      <h1 class="text-3xl font-bold text-gray-900 dark:text-white">Watchlists</h1>
      <button @click="showAddList = true" 
              class="mt-4 sm:mt-0 px-4 py-2 bg-indigo-600 text-white rounded-lg shadow hover:bg-indigo-700 transition">
        Add Watchlist
      </button>
    </div>

    <!-- Add Watchlist Modal -->
    <div v-if="showAddList" class="fixed inset-0 bg-black/50 flex justify-center items-center z-50">
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-lg w-full max-w-md p-6">
        <h2 class="text-xl font-bold mb-4 text-gray-900 dark:text-white">New Watchlist</h2>
        <input v-model="newListName" type="text" placeholder="Watchlist Name" 
               class="w-full mb-4 px-3 py-2 border rounded-lg dark:bg-gray-700 dark:text-white dark:border-gray-600 focus:outline-none focus:ring-2 focus:ring-indigo-500"/>
        <div class="flex justify-end space-x-2">
          <button @click="showAddList = false" class="px-4 py-2 bg-gray-200 dark:bg-gray-700 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition">Cancel</button>
          <button @click="addWatchlist" class="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition">Add</button>
        </div>
      </div>
    </div>

    <!-- Watchlist Tabs -->
    <div class="flex flex-wrap gap-2 mb-6">
      <button v-for="(list, index) in watchlists" :key="list.name" 
              @click="activeList = index"
              :class="activeList === index ? 'bg-indigo-600 text-white' : 'bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-200'"
              class="px-4 py-2 rounded-lg font-medium hover:bg-indigo-500 hover:text-white transition">
        {{ list.name }}
      </button>
    </div>

    <!-- Stocks Table -->
    <div v-if="currentStocks.length > 0" class="bg-white dark:bg-gray-800 rounded-xl shadow overflow-x-auto mb-6">
      <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
        <thead class="bg-gray-50 dark:bg-gray-900">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Symbol</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Price</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Market Cap</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">P/E Ratio</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Dividend Yield</th>
            <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Actions</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
          <tr v-for="stock in currentStocks" :key="stock.symbol" class="hover:bg-gray-50 dark:hover:bg-gray-900 transition">
            <td class="px-6 py-4 font-semibold text-gray-900 dark:text-white">{{ stock.symbol }}</td>
            <td class="px-6 py-4 text-gray-700 dark:text-gray-200">${{ stock.price.toFixed(2) }}</td>
            <td class="px-6 py-4 text-gray-700 dark:text-gray-200">${{ (stock.marketCap/1e9).toFixed(2) }}B</td>
            <td class="px-6 py-4 text-gray-700 dark:text-gray-200">{{ stock.peRatio.toFixed(1) }}</td>
            <td class="px-6 py-4 text-gray-700 dark:text-gray-200">{{ stock.dividendYield.toFixed(2) }}%</td>
            <td class="px-6 py-4 text-right">
              <button @click="removeStock(stock.symbol)" class="text-red-600 hover:text-red-900 dark:text-red-400 dark:hover:text-red-200 font-medium">Remove</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-else class="text-gray-500 dark:text-gray-400 italic text-center py-10">
      No stocks in this watchlist. Add some!
    </div>

    <!-- Earnings Calendar -->
    <div v-if="currentStocks.length > 0" class="mt-8">
      <h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-4">Upcoming Earnings</h2>
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead class="bg-gray-50 dark:bg-gray-900">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Symbol</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Earnings Date</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">EPS Estimate</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Previous EPS</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
            <tr v-for="stock in currentStocks" :key="stock.symbol + '-earnings'" class="hover:bg-gray-50 dark:hover:bg-gray-900 transition">
              <td class="px-6 py-4 font-semibold text-gray-900 dark:text-white">{{ stock.symbol }}</td>
              <td class="px-6 py-4 text-gray-700 dark:text-gray-200">{{ stock.earningsDate }}</td>
              <td class="px-6 py-4 text-gray-700 dark:text-gray-200">${{ stock.epsEstimate.toFixed(2) }}</td>
              <td class="px-6 py-4 text-gray-700 dark:text-gray-200">${{ stock.previousEps.toFixed(2) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Add Stock Form -->
    <div class="mt-6 flex flex-wrap gap-2 items-center">
      <input v-model="newStockSymbol" type="text" placeholder="Stock Symbol" 
             class="px-3 py-2 border rounded-lg dark:bg-gray-700 dark:text-white dark:border-gray-600 focus:outline-none focus:ring-2 focus:ring-indigo-500"/>
      <button @click="addStock" 
              class="px-4 py-2 bg-indigo-600 text-white rounded-lg shadow hover:bg-indigo-700 transition">
        Add Stock
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

// Watchlists state
const watchlists = ref([
  { name: 'Tech Giants', stocks: [
    { symbol: 'AAPL', price: 172.3, marketCap: 2.7e12, peRatio: 28.3, dividendYield: 0.6, 
      earningsDate: '2025-10-30', epsEstimate: 1.45, previousEps: 1.38 },
    { symbol: 'MSFT', price: 299.3, marketCap: 2.5e12, peRatio: 33.1, dividendYield: 0.8,
      earningsDate: '2025-11-05', epsEstimate: 2.10, previousEps: 2.05 }
  ]},
  { name: 'EV Stocks', stocks: [
    { symbol: 'TSLA', price: 645.1, marketCap: 0.65e12, peRatio: 110.2, dividendYield: 0,
      earningsDate: '2025-10-28', epsEstimate: 1.75, previousEps: 1.60 }
  ]}
])

const activeList = ref(0)
const newListName = ref('')
const showAddList = ref(false)
const newStockSymbol = ref('')

// Computed stocks for active list
const currentStocks = computed(() => watchlists.value[activeList.value].stocks)

// Functions
const addWatchlist = () => {
  if(newListName.value.trim() === '') return
  watchlists.value.push({ name: newListName.value, stocks: [] })
  newListName.value = ''
  showAddList.value = false
  activeList.value = watchlists.value.length - 1
}

const addStock = () => {
  if(newStockSymbol.value.trim() === '') return
  const symbol = newStockSymbol.value.toUpperCase()
  // Dummy fundamental and earnings data
  const newStock = {
    symbol,
    price: Math.random()*1000,
    marketCap: Math.random()*1e12,
    peRatio: (Math.random()*50).toFixed(1),
    dividendYield: (Math.random()*5).toFixed(2),
    earningsDate: '2025-11-15',
    epsEstimate: (Math.random()*5).toFixed(2),
    previousEps: (Math.random()*5).toFixed(2)
  }
  currentStocks.value.push(newStock)
  newStockSymbol.value = ''
}

const removeStock = (symbol) => {
  const idx = currentStocks.value.findIndex(s => s.symbol === symbol)
  if(idx !== -1) currentStocks.value.splice(idx, 1)
}
</script>
