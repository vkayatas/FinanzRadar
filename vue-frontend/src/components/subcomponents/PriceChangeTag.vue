<template>
  <span
    class="inline-flex flex-wrap items-center rounded-md px-2 py-1 text-[10px] sm:text-xs font-medium inset-ring"
    :class="value >= 0
      ? 'bg-green-50 text-green-700 inset-ring-green-600/20'
      : 'bg-red-50 text-red-700 inset-ring-red-600/10'"
    v-if="value !== null && value !== undefined"
  >
    <!-- Optional label -->
    <span v-if="label" class="mr-1 font-semibold">{{ label }}:</span>

    <!-- Value -->
    {{ value >= 0 ? '+' : '' }}{{ value?.toFixed(1) }}%

    <!-- Triangle indicators (can be disabled) -->
    <span
      v-if="showTriangle"
      :class="[ 
        'inline-flex items-center px-0.5 rounded-full text-xs font-medium',
        value >= 0
          ? 'text-green-700 dark:text-green-200'
          : 'text-red-700 dark:text-red-200'
      ]"
    >
      <svg
        v-if="value >= 0"
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 24 24"
        class="w-3 h-3 fill-current"
      >
        <path d="M12 4l8 16H4z" />
      </svg>
      <svg
        v-else
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 24 24"
        class="w-3 h-3 fill-current rotate-180"
      >
        <path d="M12 4l8 16H4z" />
      </svg>
    </span>
  </span>
</template>

<script setup>
defineProps({
  value: { type: Number, required: false },
  label: { type: String, default: '' },
  showTriangle: { type: Boolean, default: true } 
})
</script>
