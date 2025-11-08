<template>
  <div class="relative group flex flex-col h-full">
    <!-- Title -->
    <h3
      class="text-base md:text-base lg:text-lg font-semibold text-gray-900 dark:text-white truncate border-b border-gray-300 dark:border-gray-600 pb-1"
      :title="title"
    >
      {{ title }}
    </h3>

    <!-- Fullscreen button -->
    <button
      v-if="!hideFullscreenButton"
      @click.stop="openFullscreen()"
      class="absolute top-2 right-2 z-10 p-1 bg-white dark:bg-gray-800 rounded-full shadow
             w-6 h-6 sm:w-5 sm:h-5 md:w-6 md:h-6
             opacity-100 lg:opacity-0 lg:group-hover:opacity-100 transition-opacity"
      title="Fullscreen"
    >
      <ArrowsPointingOutIcon class="w-full h-full text-gray-600 dark:text-gray-300" />
    </button>

    <!-- Chart slot grows to fill available space -->
    <div class="flex-1 relative">
      <slot :labels="labels" :series="series" />
    </div>


    <!-- Delta Badges -->
    <div v-if="showDeltaBadges" class="flex items-center justify-center gap-1 py-1">
      <!-- Metric badge -->
      <span class="bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-200 text-xs font-semibold px-2 py-0.5 rounded-full">
        {{ props.data[0].name }}
      </span>

      <!-- Delta badges row -->
      <div class="flex items-center justify-center gap-2 flex-wrap">
        <PriceChangeTag
          v-for="(delta, label) in deltas"
          :key="label"
          :value="delta.percent"
          :label="label"
          class="flex-shrink-0"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import {computed} from 'vue'
import { ArrowsPointingOutIcon } from '@heroicons/vue/24/outline'
import PriceChangeTag from '@/components/subcomponents/PriceChangeTag.vue'
import {toEchartsDataFormat, computeDeltas} from '@/api/utils/chartData.js'

// Init props
const props = defineProps({
  title: { type: String, required: true },
  data: { type: [Array, Object], required: true },     
  labels: { type: Array, default: () => [] },          
  chartType: { type: String, required: true },  
  xAxisName: { type: String, default: "X_Axis" },  
  yAxisName: { type: String, default: "Y_Axis" },  
  xAxisType: { type: String },  
  areaStyle: { type: Boolean },        
  hideFullscreenButton: { type: Boolean, default: false },
  showDeltaBadges: { type: Boolean, default: true },
  formatCurrency: { type: String}
})

const emit = defineEmits(['fullscreen'])

// Normalized series for chart slot
const series = toEchartsDataFormat(props.data, props.title);

// Computed deltas for price change badges
const deltas = computed(() => {
  const metricData =
    Array.isArray(props.data) && props.data.length >= 1
      ? props.data[0].data
      : props.data;

  return computeDeltas(metricData, props.labels);
});

function openFullscreen() {
  emit('fullscreen', {
    title: props.title,
    data: series,           
    labels: props.labels,
    chartType: props.chartType,
    xAxisName: props.xAxisName ?? 'X_Axis',
    yAxisName: props.yAxisName ?? 'Y_Axis',
    xAxisType: props.xAxisType ?? 'value',
    areaStyle: props.areaStyle ?? null,
    formatCurrency: props.formatCurrency
  })
}

</script>
