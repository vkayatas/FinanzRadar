<template>
  <div ref="chartRef" class="w-full min-h-[25vh] md:min-h-[35vh]"></div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  labels: { type: Array, default: () => [] },
  series: {
    type: Array,
    default: () => [
      { name: 'Series 1', data: [], color: '#4F46E5' }
    ]
  },
  yAxisName: { type: String, default: 'Value' },
  xAxisLabel: { type: String, default: 'X' },
  smooth: { type: Boolean, default: true },
  areaStyle: { type: Boolean, default: false } // <- optional boolean
})

const chartRef = ref(null)
let chartInstance = null

const setOptions = () => {
  if (!chartInstance) return

  chartInstance.setOption({
    tooltip: {
      trigger: 'axis',
      formatter: (params) =>
        params.map(p => `${p.marker} ${p.seriesName}: ${p.data} <br/> ${props.xAxisLabel}: ${p.axisValue}`).join('<br/>')
    },
    legend: {
      top: 'top',
      data: props.series.map(s => s.name)
    },
    xAxis: { type: 'category', data: props.labels, axisTick: { alignWithLabel: true } },
    yAxis: { type: 'value', name: props.yAxisName },
    series: props.series.map(s => ({
      type: 'line',
      name: s.name,
      data: s.data,
      smooth: props.smooth,
      lineStyle: { color: s.color || '#4F46E5', width: 2 },
      itemStyle: { color: s.color || '#4F46E5' }, // use same color for points
      ...(props.areaStyle
  ? { areaStyle: { color: s.color + '33' } } // 20% opacity
  : {})
    })),
    grid: { left: '10%', right: '10%', bottom: '10%' }
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
