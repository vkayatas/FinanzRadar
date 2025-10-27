<template>
  <div ref="chartRef" class="w-full min-h-[20vh] md:min-h-[25vh]"></div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick, watch } from 'vue';
import * as echarts from 'echarts';

const props = defineProps({
  data: { type: Array, default: () => [] },
  labels: { type: Array, default: () => [] },
});

const chartRef = ref(null);
let chartInstance = null;

const setOptions = () => {
  if (!chartInstance) return;

  chartInstance.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
    legend: { top: 'top' },
    toolbox: {
      show: true,
      feature: {
        mark: { show: true },
        dataView: { show: true, readOnly: false },
        restore: { show: true },
        saveAsImage: { show: true },
      },
    },
    series: [
      {
        name: 'Nightingale Chart',
        type: 'pie',
        radius: [15, 100],           // inner & outer radius
        center: ['50%', '60%'],      // center in container
        roseType: 'area',            // nightingale/rose type
        itemStyle: { borderRadius: 8 },
        data: props.labels.map((label, i) => ({
          name: label,
          value: props.data[i] || 0,
        })),
      },
    ],
    grid: { left: '10%', right: '10%', bottom: '15%' },
  });
};

// Initialize chart
onMounted(async () => {
  await nextTick();
  if (!chartRef.value) return;
  chartInstance = echarts.init(chartRef.value);
  setOptions();
  window.addEventListener('resize', resizeChart);
});

// Clean up
onBeforeUnmount(() => {
  window.removeEventListener('resize', resizeChart);
  chartInstance?.dispose();
});

const resizeChart = () => chartInstance?.resize();

// Update chart if data changes
watch(() => props.data, () => setOptions());
watch(() => props.labels, () => setOptions());
</script>
