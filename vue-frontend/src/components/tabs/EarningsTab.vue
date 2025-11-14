<template>
  <!-- Main grid: responsive -->
  <div v-if="store.selectedStock">
      <div v-if="store.earnings.loading" class="text-gray-500 dark:text-gray-400">
        Loading Earnings...
      </div>
      <div v-else-if="store.earnings.error" class="text-red-500 dark:text-red-400">
        Error: {{ store.earnings.error }}
      </div>
    <div v-else-if="store.earnings" class="grid grid-cols-1 lg:grid-cols-5 gap-4 ">
      
      <!-- Left Column: DataTable (60% on lg, full width on sm) -->
    <div class="lg:col-span-3 bg-white dark:bg-gray-800 rounded-lg shadow p-4">
      <h2
        class="text-base sm:text-xl font-bold mb-4 inline-block border-b-4 border-indigo-500 dark:border-indigo-400 pb-1 w-max">
        Earnings History
      </h2>

      <div class="p-1 overflow-x-auto">
        <PrimevueDataTable
          :columns="store.earnings.columns"
          :data="store.earnings.calls"
        />
        </div>
      </div>

      <!-- Right Column: Next Earnings + Chart + Spacer -->
      <div class="lg:col-span-2 flex flex-col min-h-0 gap-4">
        <!-- Next Earnings -->
        <div class="bg-white dark:bg-gray-800 p-4 rounded-lg shadow flex-none">
          <h2 class="text-base sm:text-xl font-bold mb-4 border-b-4 border-indigo-500 dark:border-indigo-400 inline-block pb-1 w-max">
            Next Earnings
          </h2>

          <!-- Countdown & Info -->
          <div class="flex items-center justify-between mb-4">
            <span class="text-sm font-medium text-gray-600 dark:text-gray-400">Date</span>
            <span class="text-sm font-semibold text-gray-900 dark:text-indigo-300">
              {{ store.earnings.nextEarnings.date }}
              <span class="ml-2 px-2 py-0.5 text-xs font-medium bg-indigo-100 text-indigo-700 rounded-full dark:bg-indigo-900 dark:text-indigo-200">
                in {{ store.earnings.daysToNextEarnings }} days
              </span>
            </span>
          </div>

          <dl class="grid grid-cols-1 gap-y-2 text-sm">
   
            <div class="flex items-center justify-between">
              <dt class="font-medium text-gray-600 dark:text-gray-400">EPS Estimate</dt>
              <dd class="font-semibold text-gray-900 dark:text-gray-100">{{ formatCurrency(store.earnings.nextEarnings.epsEstimate) }}</dd>
            </div>
            <div class="flex items-center justify-between">
              <dt class="font-medium text-gray-600 dark:text-gray-400">Dividend Ex-Date</dt>
              <dd class="font-semibold text-gray-900 dark:text-gray-100">{{ store.earnings.nextEarnings.dividendExDate }}</dd>
            </div>
            <div class="flex items-center justify-between pb-4">
              <dt class="font-medium text-gray-600 dark:text-gray-400">Expected Dividend</dt>
              <dd class="font-semibold text-gray-900 dark:text-gray-100">{{ formatCurrency(store.earnings.nextEarnings.expectedDividend) }}</dd>
            </div>
          </dl>
          
          <div class="flex items-center justify-between pt-2 border-t border-gray-200 dark:border-gray-700">
            <span class="text-sm font-medium text-gray-600 dark:text-gray-400">
              Earnings Surprise Rate
            </span>
            <PriceChangeTag
              :value="store.earnings.earningsSurpriseRate" :showTriangle="false"
            />
          </div>

        </div>

        <!-- Earnings Overview Chart -->
        <div class="bg-white dark:bg-gray-800 p-4 rounded-lg w-full">
          <ChartSection
            :section="section"
            :stock-backend-data="store.earnings.scatterSeries"
            :show-delta-badges="false"
            class="mb-8"
          />
        </div>

        <!-- Spacer to fill remaining space -->
        <div class="flex-1"></div>
      </div>
    </div>

    <!-- DCF Evaluation Row -->
    <div v-if="false" class="grid grid-cols-1 gap-4 p-4">
      <EarningsDcfEvaluation></EarningsDcfEvaluation>
    </div>
  </div>
</template>


<script setup>
import { useStockOrchestrator } from '@/stores/stockOrchestrator';
import PrimevueDataTable from "@/components/tables/PrimevueDataTable.vue"
import EarningsDcfEvaluation from "@/components/ui/EarningsDcfEvaluation.vue"
import {formatCurrency, formatDelta} from '@/api/utils/mathUtils.js'
import PriceChangeTag from '@/components/subcomponents/PriceChangeTag.vue';
import ChartSection from '@/components/subcomponents/ChartSection.vue';

// Init store and unpack data
const store = useStockOrchestrator();
const section = {
    title: 'Earnings History',
    charts: [
      { title: 'Recent Earnings', chartType: 'scatter', metric: 'earningsHistoryScatter', xAxisName: 'Quarters', yAxisName: 'EPS', xAxisType: 'category'}
    ]
  };
</script>
