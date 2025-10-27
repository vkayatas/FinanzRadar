import { ref } from 'vue'
import { defineStore } from 'pinia'
import { stockDetailsDataMock, stockKpiGroupsDataMock } from '@/assets/stockMocks'

export const useStockInfoAndKpiStore = defineStore('stockInfoAndKpi', () => {
  const details = ref(null)
  const kpis = ref([])
  const loadedTickers = ref(new Set())

  const load = async (ticker) => {
    if (loadedTickers.value.has(ticker)) return // cached
    details.value = stockDetailsDataMock
    kpis.value = stockKpiGroupsDataMock
    loadedTickers.value.add(ticker)
  }

  return { details, kpis, load }
})
