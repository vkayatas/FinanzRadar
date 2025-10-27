// stores/watchlistStore.js
import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import {
  watchlistsMock,
  watchlistFundamentalsColumnsMock,
  watchlistEarningsColumnsMock,
  watchlistColumnsMock
} from '@/assets/stockMocks'

export const useWatchlistStore = defineStore('watchlist', () => {
  // ----- STATE -----
  const watchlists = ref([...watchlistsMock])
  const fundamentalsColumns = ref([...watchlistFundamentalsColumnsMock])
  const earningsColumns = ref([...watchlistEarningsColumnsMock])
  const watchlistColumns = ref([...watchlistColumnsMock])
  const activeIndex = ref(0)

  // ----- COMPUTED -----
  const activeWatchlist = computed(() => watchlists.value[activeIndex.value] || null)

  // ----- ACTIONS -----
  function selectWatchlist(index) {
    if (index >= 0 && index < watchlists.value.length) {
      activeIndex.value = index
    }
  }

  function createWatchlist(name) {
    const trimmedName = name.trim()
    if (trimmedName) {
      watchlists.value.push({
        name: trimmedName,
        stocks: [],
        upcomingEarnings: [],
        fundamentals: [],
        dipData: {}
      })
      activeIndex.value = watchlists.value.length - 1
    }
  }

  function deleteWatchlist(index) {
    if (index >= 0 && index < watchlists.value.length) {
      watchlists.value.splice(index, 1)
      if (activeIndex.value >= watchlists.value.length) {
        activeIndex.value = watchlists.value.length - 1
      }
    }
  }

  // Add stock and populate data from mocks if available
  function addStock(stock) {
    if (!activeWatchlist.value) return
    const exists = activeWatchlist.value.stocks.some(s => s.ticker === stock.ticker)
    if (exists) return

    activeWatchlist.value.stocks.push(stock)

    // Find the stock in mocks to copy earnings, fundamentals, dipData
    for (const mockWatchlist of watchlistsMock) {
      const mockStockFundamentals = mockWatchlist.fundamentals?.find(f => f.Ticker === stock.ticker)
      const mockStockEarnings = mockWatchlist.upcomingEarnings?.find(e => e.ticker === stock.ticker)
      const mockStockDipData = {}

      if (mockStockDipData) {
        Object.keys(mockWatchlist.dipData || {}).forEach(key => {
          const entry = mockWatchlist.dipData[key].find(d => d.ticker === stock.ticker)
          if (entry) {
            mockStockDipData[key] = [entry]
          }
        })
      }

      if (mockStockFundamentals) activeWatchlist.value.fundamentals.push(mockStockFundamentals)
      if (mockStockEarnings) activeWatchlist.value.upcomingEarnings.push(mockStockEarnings)
      if (Object.keys(mockStockDipData).length) {
        activeWatchlist.value.dipData = { ...activeWatchlist.value.dipData, ...mockStockDipData }
      }
    }
  }

  function removeStock(stock) {
    if (!activeWatchlist.value) return
    activeWatchlist.value.stocks = activeWatchlist.value.stocks.filter(s => s.ticker !== stock.ticker)
    activeWatchlist.value.upcomingEarnings = activeWatchlist.value.upcomingEarnings.filter(e => e.ticker !== stock.ticker)
    activeWatchlist.value.fundamentals = activeWatchlist.value.fundamentals.filter(f => f.Ticker !== stock.ticker)
    if (activeWatchlist.value.dipData) {
      Object.keys(activeWatchlist.value.dipData).forEach(key => {
        activeWatchlist.value.dipData[key] = activeWatchlist.value.dipData[key].filter(d => d.ticker !== stock.ticker)
      })
    }
  }

  // ----- RETURN -----
  return {
    watchlists,
    activeWatchlist,
    fundamentalsColumns,
    earningsColumns,
    watchlistColumns,
    selectWatchlist,
    createWatchlist,
    deleteWatchlist,
    addStock,
    removeStock
  }
})
