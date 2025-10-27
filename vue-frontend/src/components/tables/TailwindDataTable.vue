<template>
  <div class="overflow-x-auto">
    <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700 text-sm">
      <thead class="bg-gray-50 dark:bg-gray-700">
        <tr>
          <th
            v-for="col in columns"
            :key="col.key"
            class="px-4 py-2 text-left font-medium text-gray-600 dark:text-gray-300"
          >
            {{ col.name }}
          </th>
        </tr>
      </thead>
      <tbody class="divide-y divide-gray-100 dark:divide-gray-700">
        <tr
          v-for="(row, idx) in data"
          :key="idx"
          :class="idx % 2 === 0 
            ? 'bg-white dark:bg-gray-800 hover:bg-gray-100 dark:hover:bg-gray-600/20' 
            : 'bg-gray-50 dark:bg-gray-700/30 hover:bg-gray-100 dark:hover:bg-gray-600/40'"
        >
          <td
            v-for="col in columns"
            :key="col.key"
            class="px-4 py-2 text-gray-900 dark:text-gray-100"
          >
            {{ row[col.key] }}
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
const props = defineProps({
  columns: { type: Array, default: () => [] },
  data: { type: Array, default: () => [] }
})
</script>
