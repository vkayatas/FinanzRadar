<template>
  <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-md p-4 flex flex-col space-y-2">
    <h3 class="text-sm sm:text-xs font-bold text-gray-900 dark:text-white mb-2 pb-2 border-b border-gray-300/40 dark:border-gray-600/40">
      {{ title }}
    </h3>

    <div class="flex flex-col space-y-1">
      <div
        v-for="(kpi, index) in kpis"
        :key="index"
        class="flex justify-between py-2 border-b last:border-b-0 border-gray-300/40 dark:border-gray-600/40"
      >
        <span class="text-gray-600 dark:text-gray-300">{{ kpi.name }}</span>
        <span class="font-semibold text-gray-900 dark:text-white">{{ kpi.value }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
  defineProps({
    title: { type: String, required: true },
    kpis: { type: Array, required: true }
  })
</script>
