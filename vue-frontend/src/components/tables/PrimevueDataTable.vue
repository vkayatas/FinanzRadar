<template>
  <div class="w-full shadow-md rounded-lg min-w-0">
    <DataTable
      class="w-full"
      :value="data"
      paginator
      :rows="20"
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
          <!-- Use PriceChangeTag for delta-style values (no label, no triangle) -->
          <PriceChangeTag
            v-if="col.format === 'deltaTag'"
            :value="slotProps.data[col.key || col.field]"
            :showTriangle="false"
          />

          <!-- Format as currency -->
          <span v-else-if="col.format === 'currency'">
            {{ formatCurrency(slotProps.data[col.key || col.field]) }}
          </span>

          <!-- Default text -->
          <span v-else>
            {{ slotProps.data[col.key || col.field] }}
          </span>
        </template>
      </Column>
    </DataTable>
  </div>
</template>

<script setup>
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import PriceChangeTag from '@/components/subcomponents/PriceChangeTag.vue' 
import { formatCurrency } from '@/api/utils/mathUtils.js'

defineProps({
  columns: { type: Array, default: () => [] },
  data: { type: Array, default: () => [] },
})
</script>
