<template>
  <div class="flex items-center gap-4">
    <label class="w-48 text-sm font-medium text-gray-900 dark:text-gray-200 text-left">{{ label }}</label>
    <div class="flex items-stretch flex-1 rounded-md ring-1 ring-gray-200 dark:ring-gray-700 bg-white dark:bg-gray-800 overflow-hidden focus-within:ring-indigo-500">
      <input
        :type="type"
        :step="step"
        :min="min"
        :max="max"
        :value="modelValue"
        @input="$emit('update:modelValue', $event.target.value)"
        :disabled="disabled"
        class="h-10 flex-1 px-3 text-base text-gray-900 dark:text-gray-100 placeholder:text-gray-400 bg-transparent focus:outline-none"
      />
      <div class="flex items-center h-10 px-3 text-xs font-medium text-gray-700 dark:text-gray-200 rounded-r-md shadow-sm
                  bg-gradient-to-r from-gray-100 to-gray-200 dark:from-gray-600 dark:to-gray-700
                  transition duration-200 hover:brightness-110 hover:scale-105">
        {{ unit }}
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  label: String,
  modelValue: [String, Number],
  unit: String,
  type: { type: String, default: 'number' },
  step: Number,
  min: Number,
  max: Number,
  disabled: Boolean
});

defineEmits(['update:modelValue']);
</script>
