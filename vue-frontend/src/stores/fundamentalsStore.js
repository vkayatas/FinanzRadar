// /stores/fundamentalStore.js
import { ref } from 'vue'
import { defineStore } from 'pinia'
import { stockFundamentalDataMock } from '@/assets/stockMocks'

export const useFundamentalStore = defineStore('fundamentals', () => {
  const data = ref(null)
  const loadedTickers = ref(new Set())

  const load = async (ticker) => {
    if (loadedTickers.value.has(ticker)) return // cached
    // Replace mock with Axios call in real implementation
    data.value = stockFundamentalDataMock
    loadedTickers.value.add(ticker)
  }

  return { data, load }
})
