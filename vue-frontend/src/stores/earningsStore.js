// /stores/earningsStore.js
import { ref, computed } from 'vue';
import { defineStore } from 'pinia';
import { fetchEarnings } from '@/api/stock_sec'; // <-- make sure this exists
import { earningsColumnsMock, earningsCallsMock, earningsScatterSeriesMock, nextEarningsMock } from '@/assets/stockMocks';

const USE_MOCK_EARNINGS = false;

export const useEarningsStore = defineStore('earnings', () => {
  const columns = ref([]);
  const calls = ref([]);
  const scatterSeries = ref({ metrics: { earningsHistoryScatter: [] } });
  const nextEarnings = ref(null);
  const loadedTickers = ref(new Set());
  const loading = ref(false);
  const error = ref(null);

  const load = async (ticker) => {
    if (!ticker) return;
    //if (loadedTickers.value.has(ticker)) return; // cached

    loading.value = true;
    error.value = null;

    try {
      if (USE_MOCK_EARNINGS) {
        columns.value = earningsColumnsMock;
        calls.value = earningsCallsMock;
        scatterSeries.value = { metrics: { earningsHistoryScatter:  earningsScatterSeriesMock}}; 
        nextEarnings.value = nextEarningsMock;
      } else {
        const data = await fetchEarnings(ticker); // <-- must return { columns, calls, scatterSeries, nextEarnings }
        columns.value = data.columns || [];
        calls.value = data.calls || [];
        scatterSeries.value = { metrics: { earningsHistoryScatter:  data.scatterSeries || [] }};
        nextEarnings.value = data.nextEarnings || null;
      }
      //loadedTickers.value.add(ticker);
    } catch (err) {
      console.error("Error loading earnings:", err);
      error.value = err.message;
    } finally {
      loading.value = false;
    }
  };

  const daysToNextEarnings = computed(() => {
    if (!nextEarnings.value?.date) return null;
    const now = new Date();
    const nextDate = new Date(nextEarnings.value.date);
    const diff = nextDate - now;
    return Math.max(0, Math.ceil(diff / (1000 * 60 * 60 * 24)));
  });

  const earningsSurpriseRate = computed(() => {
    if (!scatterSeries.value?.length) return 0;
    const epsEstimateObj = scatterSeries.value.find(s => s.name === 'EPS Estimate');
    const epsActualObj = scatterSeries.value.find(s => s.name === 'EPS Actual');
    if (!epsEstimateObj || !epsActualObj) return 0;
    const epsEstimate = epsEstimateObj.data;
    const epsActual = epsActualObj.data;
    let beats = 0;
    epsActual.forEach((point, i) => {
      if (point[1] > epsEstimate[i][1]) beats++;
    });
    return Math.round((beats / epsActual.length) * 100);
  });

  return {
    columns,
    calls,
    scatterSeries,
    nextEarnings,
    daysToNextEarnings,
    earningsSurpriseRate,
    load,
    loading,
    error
  };
});
