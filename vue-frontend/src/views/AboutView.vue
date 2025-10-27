<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 p-6">
    <!-- Charts in dashboard -->
    <LineChart
      :series="revenueSeries"
      :labels="revenueLabels"
      class="w-full h-48 cursor-pointer"
      @click="openModal('line')"
    />

  <ScatterChart
    :series="scatterSeries"
    class="w-full h-48 cursor-pointer"
    @click="openModal('scatter')"
  />

    <HalfDonutChart
      :series="portfolioSeries"
      class="w-full h-[40vh] md:h-[60vh] cursor-pointer"
      @click="openModal('half-donut')"
    />

    <StackedAreaChart
      :series="stackedAreaSeries"
      :labels="stackedAreaLabels"
      class="w-full h-48"
      @click="openModal('stackedareachart')"
    />

    <StackedBarChart
      :series="stackedBarSeries"
      :labels="stackedBarLabels"
      class="w-full h-48"
      @click="openModal('stackedbarchart')"
    />

    <BarChart
      :series="revenueSeries"
      :labels="revenueLabels"
      class="w-full h-48 cursor-pointer"
      @click="openModal('bar')"
    />

    <NightingaleChart
      :series="nightingaleSeries"
      :labels="nightingaleLabels"
      class="w-full h-48 cursor-pointer"
      @click="openModal('nightingale')"
    />

    <!-- Expanded Chart Modal -->
    <div
      v-if="expandedChart.type !== null"
      class="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4 sm:p-6 overflow-auto"
    >
      <div class="bg-white dark:bg-gray-800 rounded-3xl shadow-xl w-full max-w-full sm:max-w-5xl mx-auto p-4 sm:p-6 relative">
        <button
          @click="closeModal"
          class="absolute bottom-4 right-4 px-4 py-2 bg-gray-400 text-white rounded-lg hover:bg-gray-500 z-50"
        >
          Close
        </button>

        <component
          :is="getComponentByType(expandedChart.type)"
          v-bind="getChartProps(expandedChart.type)"
          class="w-full h-[50vh] md:h-[70vh]"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import LineChart from '@/components/charts/LineChart.vue';
import BarChart from '@/components/charts/BarChart.vue';
import ScatterChart from '@/components/charts/ScatterChart.vue';
import HalfDonutChart from '@/components/charts/HalfDonutChart.vue';
import NightingaleChart from '@/components/charts/NightingaleChart.vue';
import StackedAreaChart from '@/components/charts/StackedAreaChart.vue';
import StackedBarChart from '@/components/charts/StackedBarChart.vue';

// Unified chart structures
const revenueSeries = [
  { name: 'Revenue', data: [120, 132, 101, 134, 90, 230, 210, 250, 500, 100], color: '#4F46E5' }
];
const revenueLabels = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct'];

const portfolioSeries = [
  { name: 'NVDA', value: 50, color: '#4F46E5' },
  { name: 'META', value: 25, color: '#F59E0B' },
  { name: 'AMZN', value: 15, color: '#10B981' },
  { name: 'GOOGL', value: 10, color: '#EF4444' }
];

const scatterSeries = [
  {
    name: 'Revenue',
    data: [
      [1, 120], [2, 132], [3, 101], [4, 134], [5, 90],
      [6, 230], [7, 210], [8, 250], [9, 500], [10, 100]
    ],
    color: '#4F46E5'
  },
  {
    name: 'Adjusted Revenue',
    data: [
      [1, 100], [2, 112], [3, 81], [4, 114], [5, 70],
      [6, 210], [7, 190], [8, 230], [9, 480], [10, 80]
    ],
    color: '#F59E0B'
  }
]

// Stacked Area Chart
const stackedAreaSeries = [
  { name: 'Product A', data: [120, 132, 101, 134, 90, 230, 210], color: '#4F46E5' },
  { name: 'Product B', data: [60, 72, 91, 84, 50, 130, 110], color: '#F59E0B' },
  { name: 'Product C', data: [30, 42, 51, 44, 20, 60, 50], color: '#10B981' }
];
const stackedAreaLabels = ['Jan','Feb','Mar','Apr','May','Jun','Jul'];

// Stacked Bar Chart
const stackedBarSeries = [
  { name: 'Q1', data: [120, 132, 101, 134, 90], color: '#4F46E5' },
  { name: 'Q2', data: [60, 72, 91, 84, 50], color: '#F59E0B' },
  { name: 'Q3', data: [30, 42, 51, 44, 20], color: '#10B981' }
];
const stackedBarLabels = ['Jan','Feb','Mar','Apr','May'];

// Nightingale
const nightingaleSeries = [
  { name: 'rose', data: [40, 38, 32, 30, 28, 26, 22, 18], color: '#4F46E5' }
];
const nightingaleLabels = ['rose 1','rose 2','rose 3','rose 4','rose 5','rose 6','rose 7','rose 8'];

// Modal state
const expandedChart = ref({ type: null });
const openModal = (type) => { expandedChart.value = { type }; };
const closeModal = () => { expandedChart.value = { type: null }; };

// Dynamic component mapping
const getComponentByType = (type) => {
  if (type === 'line') return LineChart;
  if (type === 'bar') return BarChart;
  if (type === 'scatter') return ScatterChart;
  if (type === 'half-donut') return HalfDonutChart;
  if (type === 'nightingale') return NightingaleChart;
  if (type === 'stackedareachart') return StackedAreaChart;
  if (type === 'stackedbarchart') return StackedBarChart;
};

// Return props using unified `series` + `labels`
const getChartProps = (type) => {
  switch(type) {
    case 'scatter':
      return { primarySeries: revenueSeries, secondarySeries: revenueSeries.map(s => ({ ...s, data: s.data.map(v => v - 20) })), xLabels: revenueLabels };
    case 'line':
    case 'bar':
      return { series: revenueSeries, labels: revenueLabels };
    case 'half-donut':
      return { series: portfolioSeries };
    case 'nightingale':
      return { series: nightingaleSeries, labels: nightingaleLabels };
    case 'stackedareachart':
      return { series: stackedAreaSeries, labels: stackedAreaLabels };
    case 'stackedbarchart':
      return { series: stackedBarSeries, labels: stackedBarLabels };
    default:
      return {};
  }
};
</script>
