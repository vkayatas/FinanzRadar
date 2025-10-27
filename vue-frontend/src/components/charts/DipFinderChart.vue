<template>
 

    <!-- Timeframe Selector -->
    <div class="mb-4 flex items-center gap-2">
      <label class="text-gray-700 dark:text-gray-300">Timeframe:</label>
      <select v-model="selectedTimeframe" @change="updateChart" 
              class="rounded border-gray-300 dark:border-gray-600 px-2 py-1 bg-white dark:bg-gray-700 text-gray-900 dark:text-white">
        <option v-for="option in timeframes" :key="option.value" :value="option.value">
          {{ option.label }}
        </option>
      </select>
    </div>

    <!-- Chart Container -->
    <div ref="chartRef" class="w-full min-h-[25vh] md:min-h-[35vh]"></div>

</template>

<script setup>
import { ref, onMounted, watch, nextTick, onBeforeUnmount } from 'vue'
import * as echarts from 'echarts'

// Props for DipFinder data
const props = defineProps({
  dipData: {
    type: Object,
    default: () => ({})
  }
})

// Timeframe options
const timeframes = [
  { label: '200 Days', value: '200D' },
  { label: 'YTD', value: 'YTD' },
  { label: '1Y', value: '1Y' },
  { label: '5Y', value: '5Y' }
]

const selectedTimeframe = ref('200D')
const chartRef = ref(null)
let chartInstance = null

// Set chart options
const setChartOptions = () => {
  if (!chartInstance) return
  const data = props.dipData[selectedTimeframe.value] || []

  chartInstance.setOption({
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: (params) => `${params[0].name}: ${params[0].value.toFixed(2)}%`
    },
    xAxis: {
      type: 'category',
      data: data.map(d => d.ticker),
      axisTick: { alignWithLabel: true }
    },
    yAxis: {
      type: 'value',
      axisLabel: { formatter: '{value}%' }
    },
    series: [
      {
        type: 'bar',
        data: data.map(d => ({
          value: d.change,
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: d.change >= 0 ? '#16a34a' : '#dc2626' },
              { offset: 1, color: d.change >= 0 ? '#4ade80' : '#f87171' }
            ])
          },
          label: {
            show: true,
            position: 'top',
            formatter: '{c}%',
            color: d.change >= 0 ? '#16a34a' : '#b91c1c'
          }
        })),
        barWidth: '50%',
        animationDuration: 800,
        animationEasing: 'cubicOut'
      }
    ],
    grid: { left: '10%', right: '10%', bottom: '15%' },
    animationDurationUpdate: 800,
    animationEasingUpdate: 'cubicOut'
  })
}

// Update chart
const updateChart = () => setChartOptions()

// Lifecycle hooks
onMounted(async () => {
  await nextTick()
  if (!chartRef.value) return
  chartInstance = echarts.init(chartRef.value)
  setChartOptions()
  window.addEventListener('resize', resizeChart)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', resizeChart)
  chartInstance?.dispose()
})

// Resize handler
const resizeChart = () => chartInstance?.resize()

// Watch for changes in timeframe or dipData
watch([selectedTimeframe, () => props.dipData], updateChart, { deep: true })
</script>
