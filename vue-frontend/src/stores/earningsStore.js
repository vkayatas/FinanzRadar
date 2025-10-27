// /stores/earningsStore.js
import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { earningsColumnsMock, earningsCallsMock, earningsScatterSeriesMock, nextEarningsMock } from '@/assets/stockMocks'

export const useEarningsStore = defineStore('earnings', () => {
  const columns = ref([])
  const calls = ref([])
  const scatterSeries = ref([])
  const nextEarnings = ref(null)
  const loadedTickers = ref(new Set())

  const load = async (ticker) => {
    if (loadedTickers.value.has(ticker)) return // cached
    columns.value = earningsColumnsMock
    calls.value = earningsCallsMock
    scatterSeries.value = earningsScatterSeriesMock
    nextEarnings.value = nextEarningsMock
    loadedTickers.value.add(ticker)
  }

  // --- Computed: Days until next earnings ---
  const daysToNextEarnings = computed(() => {
    if (!nextEarnings.value?.date) return null
    const now = new Date()
    const nextDate = new Date(nextEarnings.value.date)
    const diff = nextDate - now
    return Math.max(0, Math.ceil(diff / (1000 * 60 * 60 * 24)))
  })

  // --- Computed: Earnings surprise rate ---
  const earningsSurpriseRate = computed(() => {
    if (!scatterSeries.value || scatterSeries.value.length === 0) return 0

    const epsEstimateObj = scatterSeries.value.find(s => s.name === 'EPS Estimate')
    const epsActualObj = scatterSeries.value.find(s => s.name === 'EPS Actual')
    if (!epsEstimateObj || !epsActualObj) return 0

    const epsEstimate = epsEstimateObj.data
    const epsActual = epsActualObj.data

    let beats = 0
    epsActual.forEach((point, i) => {
      if (point[1] > epsEstimate[i][1]) beats++
    })
    return Math.round((beats / epsActual.length) * 100)
  })

  return {
    columns,
    calls,
    scatterSeries,
    nextEarnings,
    daysToNextEarnings,
    earningsSurpriseRate,
    load,
  }
})
