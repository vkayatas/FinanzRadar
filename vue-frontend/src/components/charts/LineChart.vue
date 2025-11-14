<template>
  <div ref="chartRef" class="w-full min-h-[25vh] md:min-h-[35vh]"></div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import * as echarts from 'echarts'
import { formatCurrency } from '@/api/utils/mathUtils.js'

const props = defineProps({
  labels: { type: Array, default: () => [] },
  series: {
    type: Array,
    default: () => [
      { name: 'Series 1', data: [], color: '#4F46E5' }
    ]
  },
  yAxisName: { type: String, default: 'Value' },
  xAxisLabel: { type: String, default: 'Date' },
  smooth: { type: Boolean, default: true },
  formatCurrency: { type: String },
  areaStyle: { type: Boolean, default: false } // <- optional boolean
})

const chartRef = ref(null)
let chartInstance = null

const setOptions = () => {
  if (!chartInstance) return

  chartInstance.setOption({
    tooltip: {
      trigger: 'axis',
      formatter: (params) => {
        if (!params || !params.length) return '';

        // Show x-axis label once
        const xLabelLine = `${props.xAxisLabel}: ${params[0].axisValue}`;

        // Show each series' data value
        const dataLines = params.map(p => {
          const value = formatCurrency(p.data, props.formatCurrency);
          return `${p.marker} ${p.seriesName}: ${value}`;
        });

        // Combine label and data
        return `${xLabelLine}<br/>${dataLines.join('<br/>')}`;
      },
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
