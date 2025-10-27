<template>
  <div class="w-full overflow-x-auto shadow-md rounded-lg min-w-0 bg-white dark:bg-gray-800 p-4">
    <!-- Toolbar -->
    <div class="flex justify-between items-center mb-3">
      <h2 class="text-lg font-semibold text-gray-900 dark:text-gray-100">Stocks</h2>
      <button
        class="flex items-center gap-2 px-3 py-2 bg-indigo-500 text-white rounded hover:bg-indigo-600"
        @click="$emit('add')"
      >
        <PlusIcon class="w-5 h-5" />
        Add Stock
      </button>
    </div>

    <!-- PrimeVue DataTable -->
    <DataTable
      class="w-full"
      :value="data"
      paginator
      :rows="rowsPerPage"
      removableSort
      :rowsPerPageOptions="[10, 20, 50, 100]"
      responsiveLayout="scroll"
      stripedRows
      size="small"
    >
      <!-- Dynamic Columns -->
      <Column
        v-for="col in columns"
        :key="col.key || col.field || col.name"
        :field="col.key || col.field"
        :header="col.name || col.header"
        :sortable="col.sortable !== false"
        :style="{ width: col.width || 'auto' }"
      >
        <template #body="slotProps">
          <span v-if="col.format === 'deltaTag'">
            <Tag
              :value="formatDelta(slotProps.data[col.key || col.field])"
              :severity="getSeverity(slotProps.data[col.key || col.field])"
              class="text-sm"
            />
          </span>
          <span v-else-if="col.format === 'currency'">
            {{ formatCurrency(slotProps.data[col.key || col.field]) }}
          </span>
          <span v-else>
            {{ slotProps.data[col.key || col.field] }}
          </span>
        </template>
      </Column>

      <!-- Actions Column -->
      <Column header="Actions" :style="{ width: '4rem' }">
        <template #body="slotProps">
          <button
            class="text-red-500 hover:text-red-600"
            @click="$emit('remove', slotProps.data)"
          >
            <TrashIcon class="w-5 h-5" />
          </button>
        </template>
      </Column>
    </DataTable>
  </div>
</template>

<script setup>
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Tag from 'primevue/tag';
import { TrashIcon, PlusIcon } from '@heroicons/vue/24/outline';
import { formatCurrency, getSeverity, formatDelta } from '@/api/utils/mathUtils.js';

const props = defineProps({
  columns: { type: Array, default: () => [] },
  data: { type: Array, default: () => [] },
  rowsPerPage: { type: Number, default: 20 },
});
</script>
