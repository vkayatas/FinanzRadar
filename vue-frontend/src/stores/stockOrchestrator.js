// /stores/stockOrchestrator.js
import { ref, watch } from 'vue'
import { defineStore } from 'pinia'
import { useFundamentalStore } from './fundamentalsStore'
import { useEarningsStore } from './earningsStore'
import { useStockInfoAndKpiStore } from './infoAndKpisStore'

export const useStockOrchestrator = defineStore('stockOrchestrator', () => {
  // selected stock state
  const selectedStock = ref(null)

  // sub-stores
  const fundamentals = useFundamentalStore()
  const earnings = useEarningsStore()
  const stockInfo = useStockInfoAndKpiStore()

  // track which tickers have been loaded
  const loadedTickers = ref(new Set())

  // internal load function
  const _loadTickerData = async (ticker) => {
    if (loadedTickers.value.has(ticker)) return
    await Promise.all([
      fundamentals.load(ticker),
      earnings.load(ticker),
      stockInfo.load(ticker)
    ])
    loadedTickers.value.add(ticker)
  }

  // auto-load when selectedStock changes
  watch(
    selectedStock,
    (newStock) => {
      if (newStock?.symbol) _loadTickerData(newStock.symbol)
    },
    { immediate: true }
  )

  // optional: manual refresh
  const refreshSelectedStock = async () => {
    if (!selectedStock.value?.symbol) return
    // clear cache for this ticker
    loadedTickers.value.delete(selectedStock.value.symbol)
    await _loadTickerData(selectedStock.value.symbol)
  }

  return {
    selectedStock,
    fundamentals,
    earnings,
    stockInfo,
    refreshSelectedStock, // clears cache
  }
})
