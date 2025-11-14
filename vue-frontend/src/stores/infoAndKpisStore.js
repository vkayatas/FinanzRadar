// /stores/stockInfoAndKpiStore.js
import { ref } from 'vue';
import { defineStore } from 'pinia';
import { stockDetailsDataMock, stockKpiGroupsDataMock } from '@/assets/stockMocks';
import { fetchStockInfo, fetchKpis } from '@/api/stock_sec'; 

// 🔧 Toggle this flag to use mock or live API
const USE_MOCK_STOCK_INFO = false;

export const useStockInfoAndKpiStore = defineStore('stockInfoAndKpi', () => {
  const details = ref(null);
  const kpis = ref([]);
  const loadedTickers = ref(new Set());
  const loading = ref(false);
  const error = ref(null);

  const load = async (ticker) => {
    ticker = ticker.toUpperCase();
    //if (loadedTickers.value.has(ticker)) return; // ✅ cache hit

    loading.value = true;
    error.value = null;

    try {
      let stockDetails;
      let stockKpis;

      if (USE_MOCK_STOCK_INFO) {
        console.log(`[Mock] Loading stock info for ${ticker}`);
        stockDetails = stockDetailsDataMock;
        stockKpis = stockKpiGroupsDataMock;
      } else {
        console.log(`[API] Fetching stock info for ${ticker}`);

        // FastAPI calls
        stockDetails = await fetchStockInfo(ticker); 
        stockKpis = await fetchKpis(ticker);
      }

      details.value = stockDetails;
      kpis.value = stockKpis;
      //loadedTickers.value.add(ticker);
    } catch (err) {
      console.error("Error loading stock info:", err);
      error.value = err.message || String(err);
    } finally {
      loading.value = false;
    }
  };

  return { details, kpis, load, loading, error };
});
