// /stores/fundamentalStore.js
import { ref } from "vue";
import { defineStore } from "pinia";
import { fetchFundamentals } from "@/api/stock_sec";
import { stockFundamentalDataMock } from '@/assets/stockMocks'

// 🔧 Toggle this flag to use mock or live API
const USE_MOCK_FUNDAMENTALS = false; // set to false to use FastAPI
const DEFAULT_FORM_TYPE = "10-K"; 

export const useFundamentalStore = defineStore("fundamentals", () => {
  const data = ref(null);
  const loadedTickers = ref(new Set());
  const loading = ref(false);
  const error = ref(null);

  const load = async (ticker) => {
    ticker = ticker.toUpperCase();
    //if (loadedTickers.value.has(ticker)) return; // ✅ cache hit

    loading.value = true;
    error.value = null;

    try {
      let fundamentals;
      if (USE_MOCK_FUNDAMENTALS) {
        console.log(`[Mock] Loading fundamentals for ${ticker}`);
        fundamentals = stockFundamentalDataMock;
      } else {
        console.log(`[API] Fetching fundamentals for ${ticker} (${DEFAULT_FORM_TYPE})`);
        fundamentals = await fetchFundamentals(ticker, DEFAULT_FORM_TYPE);
      }
      data.value = fundamentals;
      //loadedTickers.value.add(ticker);
    } catch (err) {
      console.error("Error loading fundamentals:", err);
      error.value = err.message;
    } finally {
      loading.value = false;
    }
  };

  return { data, load, loading, error };
});
