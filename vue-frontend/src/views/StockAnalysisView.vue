<template>
  <div class="bg-gray-50 dark:bg-gray-900 min-h-screen">
    <!-- Page grid -->
    <div class="grid grid-rows-[auto,auto,1fr] gap-6">
      
      <!-- Feature 1: Header -->
      <div class="row-start-1 text-center">
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white">Stock Analysis</h1>
        <p class="text-gray-600 dark:text-gray-300 mt-2">
          Search for a company or ticker symbol to analyze its fundamentals and performance.
        </p>
      </div>

      <!-- Feature 2: Autocomplete stock ticker search -->
      <div class="row-start-2 w-full sm:w-[70vw] md:w-[40vw] mx-auto">
        <StockSearchAutocomplete />
      </div>

      <!-- Feature 3: Basic stock details and price development -->
      <div class="row-start-3 grid grid-cols-1 gap-8 w-full pt-1 md:pt-4">
          <StockDetails />
      </div>

      <!-- Feature 4: Basic stock KPIs -->
      <div class="row-start-4 grid grid-cols-1 gap-8 w-full pt-1 md:pt-6">
          <StockKpiGroup />
      </div>

      <!-- Feature 5: Visualizations -->
      <div class="row-start-5 grid grid-cols-1 gap-8 w-full pt-1 md:pt-6">
          <StockAnalysisViewTabContent />
      </div>

    </div>
  </div>
</template>

<script setup>
import StockSearchAutocomplete from '@/components/subcomponents/StockSearchAutocomplete.vue'
import StockDetails from '@/components/ui/StockDetails.vue'
import StockKpiGroup from '@/components/ui/StockKpiGroup.vue'
import StockAnalysisViewTabContent from '@/components/ui/StockAnalysisViewTabContent.vue'
</script>
