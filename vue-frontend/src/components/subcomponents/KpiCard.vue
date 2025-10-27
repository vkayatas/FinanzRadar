<template>
  <div class="bg-white dark:bg-gray-800 rounded-xl shadow p-4 text-center">
    <h3 class="text-sm text-gray-500 dark:text-gray-400">{{ title }}</h3>
    <p class="mt-2 text-xl font-semibold text-gray-900 dark:text-white">{{ value }}</p>
  </div>
</template>

<script setup>
defineProps({
  title: String,
  value: String
})
</script>
