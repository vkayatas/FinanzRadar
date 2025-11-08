<template>
  <div class="mb-8">
    <h2
      class="text-base sm:text-xl font-bold mb-4 border-b-4 border-indigo-500 dark:border-indigo-400 inline-block pb-1"
    >
      {{ section.title }}
    </h2>
    <div :class="gridClass">
      <div
        v-for="(chart, idx) in processedCharts"
        :key="idx"
        class="bg-white dark:bg-gray-800 rounded-xl shadow p-3"
      >
        <ChartCard
          :title="chart.title"
          :data="chart.data"
          :labels="chart.labels"
          :chartType="chart.chartType"
          :xAxisName="chart.xAxisName"
          :yAxisName="chart.yAxisName"
          :xAxisType="chart.xAxisType"
          :areaStyle="chart.areaStyle"
          :showDeltaBadges="props.showDeltaBadges"
          @fullscreen="openFullscreen"
          class="flex-1"
        >
          <template #default="{ labels, series }">
            <component
              :is="chart.component"
              :labels="labels"
              :series="series"
              :yAxisName="chart.yAxisName"
              :xAxisName="chart.xAxisName"
              :xAxisType="chart.xAxisType"
              :areaStyle="chart.areaStyle"
              :chartType="chart.chartType"
              :showDeltaBadges="props.showDeltaBadges"
              :formatCurrency="chart.formatCurrency" 
            />
          </template>
        </ChartCard>
      </div>
    </div>

    <!-- Fullscreen modal -->
    <ChartFullscreenModal ref="fullscreenModalState" />
  </div>
</template>

<script setup>
import { ref, computed } from "vue";
import ChartFullscreenModal from '@/components/subcomponents/ChartFullscreenModal.vue';
import ChartCard from "@/components/subcomponents/ChartCard.vue";
import { buildChartData } from "@/api/utils/chartData.js";
import { chartMap } from "@/api/utils/chartMap.js";

// Init props
const props = defineProps({
  section: { type: Object, required: true },
  stockBackendData: { type: Object, required: true },
  forceSingleColumn: { type: Boolean, default: false }, 
  showDeltaBadges: { type: Boolean, default: true } 
});

// process input data to charts format
const processedCharts = computed(() =>
  props.section.charts.map(chart => {
    const metrics = chart.metrics || [{ metric: chart.metric, color: chart.color }];
    const series = metrics
      .map(m => buildChartData(props.stockBackendData, m.metric, m.color, chart.chartType))
      .flat() 
      .filter(Boolean);

    return {
      ...chart,
      data: series,
      labels: series.length ? series[0].labels : [],
      component: chartMap[chart.chartType],
      xAxisName: chart.xAxisName || 'X',
      yAxisName: chart.yAxisName || 'Y',
      xAxisType: chart.xAxisType || 'value',
      areaStyle: chart.areaStyle || null,
      showDeltaBadges: props.showDeltaBadges,
      formatCurrency: chart.formatCurrency
    };
  })
);

// Dynamic grid class
const gridClass = computed(() =>
  props.forceSingleColumn || processedCharts.value.length === 1
    ? "grid grid-cols-1 gap-6"
    : "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
);

// Fullscreen modal handling
const fullscreenModalState = ref(null);
function openFullscreen(chart) {
  fullscreenModalState.value.open({
    title: chart.title,
    data: chart.data,
    labels: chart.labels,
    chartType: chart.chartType,
    xAxisName: chart.xAxisName,
    yAxisName: chart.yAxisName,
    xAxisType: chart.xAxisType,
    areaStyle: chart.areaStyle,
    formatCurrency: chart.formatCurrency
  });
}
</script>
