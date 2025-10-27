<template>
  <div
    v-if="store.selectedStock"
    class="bg-gray-50 dark:bg-gray-900 p-4 rounded-2xl shadow-lg"
  >
    <div
      class="flex overflow-x-auto snap-x snap-mandatory border-b border-gray-300 dark:border-gray-600 mb-4"
    >
      <button
        v-for="tab in tabs"
        :key="tab"
        @click="!disabledTabs.includes(tab) && (activeTab = tab)"
        :disabled="disabledTabs.includes(tab)"
        :class="[
          'snap-start mx-2 px-3 py-2 font-semibold rounded-t-lg whitespace-nowrap flex-shrink-0 transition-colors duration-150 flex items-center space-x-1',
          activeTab === tab
            ? 'bg-white dark:bg-gray-800 text-gray-900 dark:text-white shadow'
            : 'text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white',
          disabledTabs.includes(tab)
            ? 'opacity-60 cursor-not-allowed hover:text-gray-500 dark:hover:text-gray-400'
            : ''
        ]"
      >
        <span>{{ tab }}</span>

        <!-- Coming Soon badge for disabled tabs -->
        <span
          v-if="disabledTabs.includes(tab)"
          class="ml-1 px-1.5 py-0.5 text-[10px] font-medium rounded-full bg-gray-200 dark:bg-gray-700 text-gray-600 dark:text-gray-300"
        >
          Coming Soon
        </span>
      </button>
    </div>

    <!-- Fundamental Tab -->
    <div v-if="activeTab === 'Fundamental'">
      <ChartSection
        v-for="(section, key) in filteredSectionConfigs"
        :key="key"
        :section="section"
        :stock-backend-data="store.fundamentals.data"
        :show-delta-badges="true"
        class="mb-8"
      />
    </div>

    <!-- Earnings Tab -->
    <div v-if="activeTab === 'Earnings'">
      <EarningsTab />
    </div>
  </div>
</template>


<script setup>
import { ref, computed } from 'vue';
import { useStockOrchestrator } from '@/stores/stockOrchestrator';
import ChartSection from '@/components/subcomponents/ChartSection.vue';
import EarningsTab from '@/components/tabs/EarningsTab.vue';
import { sectionConfigs } from "@/api/utils/chartData.js";

const store = useStockOrchestrator();
const tabs = ['Fundamental', 'Earnings', 'Overview', 'Competition'];
const disabledTabs = ['Overview', 'Competition']; // 👈 mark tabs as future features
const activeTab = ref('Fundamental');

// computed filtered sections
const filteredSectionConfigs = computed(() => {
  const metricsAvailable = Object.keys(store.fundamentals.data.metrics);
  const result = {};
  for (const [sectionKey, section] of Object.entries(sectionConfigs)) {
    const charts = section.charts
      .map(chart => {
        if (chart.metric) {
          return metricsAvailable.includes(chart.metric) ? chart : null;
        }
        if (chart.metrics) {
          const filteredMetrics = chart.metrics.filter(m => metricsAvailable.includes(m.metric));
          return filteredMetrics.length ? { ...chart, metrics: filteredMetrics } : null;
        }
        return null;
      })
      .filter(Boolean);

    if (charts.length) {
      result[sectionKey] = { ...section, charts };
    }
  }
  return result;
});
</script>
