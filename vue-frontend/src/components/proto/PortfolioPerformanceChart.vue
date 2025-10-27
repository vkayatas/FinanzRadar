<template>
  <div class="bg-white dark:bg-gray-800 rounded-xl shadow p-4">
    <!-- Title -->
    <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Performance</h2>

    <!-- Portfolio Info Flex -->
    <div class="flex items-center mb-4">
      <!-- Portfolio Value -->
      <div class="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white mr-4">
        {{ formatCurrency(currentValue) }}
      </div>

      <!-- Date + Change -->
      <div class="flex flex-col justify-center">
        <div class="text-gray-500 dark:text-gray-300 text-sm sm:text-base">{{ currentLabel }}</div>
        <PriceChangeTag :value="currentChange" label="Change" />
      </div>
    </div>

    <!-- Chart -->
    <div ref="chartRef" class="w-full min-h-[25vh] md:min-h-[35vh]"></div>
  </div>
</template>



<script setup>
import { ref, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import * as echarts from 'echarts'
import PriceChangeTag from '@/components/subcomponents/PriceChangeTag.vue'

const props = defineProps({
  labels: { type: Array, default: () => [] },
  data: { type: Array, default: () => [] }, // daily portfolio values
  smooth: { type: Boolean, default: true },
  areaStyle: { type: Boolean, default: true }
})

const chartRef = ref(null)
let chartInstance = null

const currentValue = ref(props.data[props.data.length - 1] || 0)
const currentLabel = ref(props.labels[props.labels.length - 1] || '')
const currentChange = ref(
  props.data.length ? ((currentValue.value - props.data[0]) / props.data[0] * 100) : 0
)

const formatCurrency = (value) =>
  new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(value)

const setOptions = () => {
  if (!chartInstance || !props.data.length) return

  const start = props.data[0]
  const last = props.data[props.data.length - 1]
  const color = last >= start ? '#16a34a' : '#dc2626'

  chartInstance.setOption({
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'line' },
      formatter: (params) => {
        const index = params[0].dataIndex
        currentValue.value = params[0].data
        currentLabel.value = props.labels[index]
        currentChange.value = ((currentValue.value - start) / start * 100)
        return `${props.labels[index]}<br/>Value: ${formatCurrency(params[0].data)}<br/>Change: ${currentChange.value.toFixed(2)}%`
      }
    },
    xAxis: { type: 'category', data: props.labels, axisTick: { alignWithLabel: true } },
    yAxis: { type: 'value', name: 'Portfolio Value' },
    series: [
      {
        type: 'line',
        data: props.data,
        smooth: props.smooth,
        lineStyle: { color, width: 2 },
        showSymbol: false,
        areaStyle: props.areaStyle ? { color: color + '33' } : undefined
      }
    ],
    grid: { left: '10%', right: '10%', bottom: '15%' }
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

watch(() => [props.data, props.labels], setOptions, { deep: true })
</script>
