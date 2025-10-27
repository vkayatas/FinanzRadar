<template>
  <!-- Always fills parent but respects height constraints -->
  <div ref="chartRef" class="w-full h-full min-h-[30vh]"></div>
</template>


<script setup>
import { ref, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  series: {
    type: Array,
    default: () => [
      { name: 'Series 1', data: [], color: '#4F46E5' }
    ]
  },
  xAxisName: { type: String, default: 'X_Default' },
  yAxisName: { type: String, default: 'Y_Default' },

  /**
   * xAxisType Default = 'value' (numeric integers)
   * Can be set to 'category' for labels like "2025 Q1"
   */
  xAxisType: {
    type: String,
    default: 'value',
    validator: v => ['value', 'category'].includes(v)
  },

  symbolSize: { type: Number, default: 12 },
  grid: { type: Object, default: () => ({ left: '10%', right: '10%', bottom: '15%' }) }
})

const chartRef = ref(null)
let chartInstance = null

const setChartOptions = () => {
  if (!chartInstance) return

  const isCategory = props.xAxisType === 'category'
  const categories = isCategory
    ? Array.from(new Set(props.series.flatMap(s => s.data.map(d => d[0]))))
    : undefined

  chartInstance.setOption({
    tooltip: {
      trigger: 'axis',
      formatter: params => {
        return params
          .map(p => `${p.marker} ${p.seriesName}: ${p.value[1]}`)
          .join('<br/>')
      }
    },
    xAxis: {
      type: props.xAxisType,
      name: props.xAxisName,
      data: categories
    },
    yAxis: {
      type: 'value',
      name: props.yAxisName
    },
    grid: props.grid,
    series: props.series.map(s => ({
      name: s.name,
      type: 'scatter',
      data: s.data,
      symbolSize: props.symbolSize,
      itemStyle: { color: s.color || '#4F46E5' }
    }))
  })
}

const resizeChart = () => chartInstance?.resize()

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

watch(() => props.series, setChartOptions, { deep: true })
watch(() => props.xAxisType, setChartOptions)
</script>
