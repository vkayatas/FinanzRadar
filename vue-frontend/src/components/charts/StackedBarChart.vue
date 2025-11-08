<template>
  <div ref="chartRef" class="w-full h-full min-h-[25vh] md:min-h-[35vh]"></div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch, nextTick } from 'vue';
import { formatCurrency } from '@/api/utils/mathUtils.js'
import * as echarts from 'echarts';

const props = defineProps({
  labels: { type: Array, default: () => [] },
  series: { type: Array, default: () => [] }, // [{ name, data, color }]
  yAxisName: { type: String, default: 'Value' },
  xAxisLabel: { type: String, default: 'Category' }
});

const chartRef = ref(null);
let chartInstance = null;

const setOptions = () => {
  if (!chartInstance) return;

  chartInstance.setOption({
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: (params) =>
        params.map(p => `${p.marker} ${p.seriesName}: ${formatCurrency(p.data)} <br/> ${props.xAxisLabel}: ${p.axisValue}`).join('<br/>')
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
      stack: 'total',
      data: s.data,
      itemStyle: { color: s.color || '#4F46E5' }
    })),
    grid: { left: '10%', right: '10%', bottom: '10%', top: '15%'}
  });
};

onMounted(async () => {
  await nextTick();
  if (!chartRef.value) return;
  chartInstance = echarts.init(chartRef.value);
  setOptions();
  window.addEventListener('resize', resizeChart);
});

onBeforeUnmount(() => {
  window.removeEventListener('resize', resizeChart);
  chartInstance?.dispose();
});

const resizeChart = () => chartInstance?.resize();

watch(() => [props.series, props.labels], setOptions, { deep: true });
</script>
