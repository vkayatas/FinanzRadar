<template>
  <h2
    class="text-base sm:text-xl font-bold mb-4 border-b-4 border-indigo-500 dark:border-indigo-400 inline-block pb-1"
  >
    {{ title }}
  </h2>
</template>

<script setup>
const props = defineProps({
  title: {
    type: String,
    required: true
  }
})
</script>
