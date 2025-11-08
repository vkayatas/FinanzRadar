<template>
  <div ref="chartRef" class="w-full min-h-[25vh] md:min-h-[35vh] h-full "></div>
</template>

<script setup>
import { formatCurrency } from '@/api/utils/mathUtils.js'
import { ref, onMounted, watch, nextTick, onBeforeUnmount } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  labels: { type: Array, default: () => [] },

  // Multiple series: [{ name, data, color }]
  series: {
    type: Array,
    default: () => [{ name: 'Series 1', data: [], color: '#4F46E5' }]
  },

  yAxisName: { type: String, default: 'Value' },
  xAxisLabel: { type: String, default: 'Category' },
  grid: { type: Object, default: () => ({ left: '10%', right: '10%', bottom: '10%' }) },
  formatCurrency: { type: String },
  barWidth: { type: String, default: '40%' } // smaller width to fit multiple bars side-by-side
})

const chartRef = ref(null)
let chartInstance = null

const setOptions = () => {
  if (!chartInstance) return

  chartInstance.setOption({
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: (params) =>
        params
          .map(p => {
            const value = formatCurrency(p.data, props.formatCurrency) 
            return `${p.marker} ${p.seriesName}: ${value} <br/> ${props.xAxisLabel}: ${p.axisValue}`})
          .join('<br/>')
    },
    legend: {
      top: 'top',
      data: props.series.map(s => s.name)
    },
    xAxis: {
      type: 'category',
      data: props.labels,
      axisTick: { alignWithLabel: true }
    },
    yAxis: {
      type: 'value',
      name: props.yAxisName
    },
    series: props.series.map(s => ({
      name: s.name,
      type: 'bar',
      data: s.data,
      barWidth: props.barWidth,
      itemStyle: { color: s.color || '#4F46E5' },
      barGap: 0,           // bars appear side-by-side
      barCategoryGap: '30%' // spacing between bar groups
    })),
    grid: props.grid
  })
}

onMounted(async () => {
  await nextTick()
  if (!chartRef.value) return
  chartInstance = echarts.init(chartRef.value)
  setOptions()
  window.addEventListener('resize', resizeChart)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', resizeChart)
  chartInstance?.dispose()
})

const resizeChart = () => chartInstance?.resize()

watch(() => [props.series, props.labels], setOptions, { deep: true })
</script>
