<template>
  <div ref="chartRef" class="w-full min-h-[20vh] md:min-h-[25vh]"></div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick, watch } from 'vue';
import * as echarts from 'echarts';

const props = defineProps({
  series: { 
    type: Array, 
    default: () => [{ name: 'Item 1', value: 50, color: '#4F46E5' }] 
  },
  startAngle: { type: Number, default: 180 },  // for half-donut
  endAngle: { type: Number, default: 360 }
});

const chartRef = ref(null);
let chartInstance = null;

const setOptions = () => {
  if (!chartInstance) return;

  chartInstance.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {c}%' },
    legend: { top: '5%', left: 'center' },
    series: [
      {
        type: 'pie',
        radius: ['50%', '90%'],       // donut thickness
        center: ['50%', '75%'],
        startAngle: props.startAngle,
        endAngle: props.endAngle,
        label: { show: true, position: 'inside', formatter: '{d}%' },
        data: props.series.map(item => ({
          name: item.name,
          value: item.value,
          itemStyle: { color: item.color || '#4F46E5' }
        }))
      }
    ]
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

watch(() => props.series, setOptions, { deep: true });
</script>
