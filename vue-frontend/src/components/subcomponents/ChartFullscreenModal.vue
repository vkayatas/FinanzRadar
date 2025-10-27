<template>
  <TransitionRoot as="template" :show="show" @update:show="$emit('update:show', $event)">
    <Dialog
      as="div"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4"
      @close="close"
    >
      <TransitionChild
        enter="transition ease-out duration-200"
        enter-from="opacity-0 scale-95"
        enter-to="opacity-100 scale-100"
        leave="transition ease-in duration-150"
        leave-from="opacity-100 scale-100"
        leave-to="opacity-0 scale-95"
      >
        <DialogPanel
          class="bg-white dark:bg-gray-800 rounded-xl shadow-lg
                 w-[90vw] sm:w-[95vw] md:w-[90vw] lg:w-[95vw]
                 h-[85vh] sm:h-[88vh] md:h-[90vh] lg:h-[90vh]
                 p-4 relative flex flex-col"
        >
          <!-- Use all chart props from payload -->
          <ChartCard
            :title="title"
            :data="series"
            :labels="labels"
            :chart-type="chartType"
            :x-axis-name="xAxisName"
            :y-axis-name="yAxisName"
            :x-axis-type="xAxisType"
            :area-style="areaStyle"
            :hide-fullscreen-button="true"
            :showDeltaBadges="showDeltaBadges"
          >
            <component :is="chartComponent" v-bind="chartProps" class="w-full h-full" />
          </ChartCard>

          <button
            @click="close"
            class="absolute top-4 right-4 text-gray-500 hover:text-gray-900 dark:hover:text-white"
            aria-label="Close"
          >
            ✕
          </button>
        </DialogPanel>
      </TransitionChild>
    </Dialog>
  </TransitionRoot>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Dialog, DialogPanel, TransitionChild, TransitionRoot } from '@headlessui/vue'
import ChartCard from '@/components/subcomponents/ChartCard.vue'
import LineChart from '@/components/charts/LineChart.vue'
import StackedAreaChart from '@/components/charts/StackedAreaChart.vue'
import StackedBarChart from '@/components/charts/StackedBarChart.vue'
import BarChart from '@/components/charts/BarChart.vue'
import ScatterChart from '@/components/charts/ScatterChart.vue'

// Chart state
const show = ref(false)
const title = ref('')
const series = ref([])
const labels = ref([])
const chartType = ref('')
const xAxisName = ref('X_Axis')
const yAxisName = ref('Y_Axis')
const xAxisType = ref('value')
const areaStyle = ref(null)
const showDeltaBadges = ref()

// Chart component mapping
const chartComponent = computed(() => {
  if (chartType.value === 'line') return LineChart
  if (chartType.value === 'area') return StackedAreaChart
  if (chartType.value === 'bar') return BarChart
  if (chartType.value === 'stackedbar') return StackedBarChart
  if (chartType.value === 'scatter') return ScatterChart
  return LineChart
})

// Bind all chart props for the component slot
const chartProps = computed(() => ({
  series: series.value,
  labels: labels.value,
  xAxisName: xAxisName.value,
  yAxisName: yAxisName.value,
  xAxisType: xAxisType.value,
  areaStyle: areaStyle.value
}))

// Open modal with full chart payload
function open(payload) {
  title.value = payload.title
  series.value = payload.data
  labels.value = payload.labels
  chartType.value = payload.chartType
  xAxisName.value = payload.xAxisName ?? 'X_Axis'
  yAxisName.value = payload.yAxisName ?? 'Y_Axis'
  xAxisType.value = payload.xAxisType ?? 'value'
  areaStyle.value = payload.areaStyle ?? null
  showDeltaBadges.value = payload.showDeltaBadges 
  show.value = true
}

// Close modal
function close() {
  show.value = false
}

// Expose functions to parent
defineExpose({ open, close })
</script>
