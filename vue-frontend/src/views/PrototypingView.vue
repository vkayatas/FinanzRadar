<template>
  <div class="bg-gray-50 dark:bg-gray-900 min-h-screen p-4">

    <!-- Header -->
    <div class="text-center mb-6">
      <h1 class="text-3xl font-bold text-gray-900 dark:text-white">
        Portfolio: {{ activePortfolio?.name || 'Select a Portfolio' }}
      </h1>
      <p class="text-gray-600 dark:text-gray-300 mt-2">
        Track your portfolio performance, holdings, dividends, and transactions.
      </p>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-[250px_1fr] gap-4 items-start">

      <!-- Sidebar -->
      <aside class="bg-white dark:bg-gray-800 rounded-xl shadow-md p-4 flex flex-col sticky top-4 max-h-[calc(100vh-2rem)]">
        <SectionTitle title="Your Portfolios" />
        <div class="mt-2 flex-1 overflow-y-auto space-y-2 pr-1">
          <div 
            v-for="(portfolio, index) in portfolios" 
            :key="index"
            class="flex items-center justify-between p-2 rounded hover:bg-gray-100 dark:hover:bg-gray-700 cursor-pointer"
            @click="selectPortfolio(index)"
            :class="activeIndex === index ? 'bg-gray-200 dark:bg-gray-700 font-semibold' : ''"
          >
            <span>{{ portfolio.name }}</span>
          </div>
        </div>

        <!-- Button always at bottom -->
        <div class="mt-4 pt-2 border-t border-gray-200 dark:border-gray-700">
          <button 
            class="w-full flex items-center justify-center gap-2 px-3 py-2 bg-indigo-500 text-white rounded hover:bg-indigo-600"
            @click="newPortfolioOpen = true"
          >
            <PlusIcon class="w-5 h-5" />
            New Portfolio
          </button>
        </div>
      </aside>


      <!-- Main Content -->
      <main class="flex flex-col gap-6">

        <!-- KPI Cards -->
        <PortfolioKpiCards :portfolio="activePortfolio" />

        <!-- Tabs -->
        <div>
          <div class="flex overflow-x-auto snap-x snap-mandatory border-b border-gray-300 dark:border-gray-600 mb-4">
            <button
              v-for="tab in tabs"
              :key="tab"
              @click="activeTab = tab"
              :class="[
                'snap-start mx-2 px-3 py-2 font-semibold rounded-t-lg whitespace-nowrap flex-shrink-0 text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors duration-150',
                activeTab === tab ? 'bg-white dark:bg-gray-800 text-gray-900 dark:text-white shadow' : ''
              ]"
            >
              {{ tab }}
            </button>
          </div>

          <!-- Tab Contents -->
          <div>
            <!-- Overview Tab -->
            <div v-if="activeTab === 'Overview'" class="space-y-6">
              
            <PortfolioPerformanceChart
              :labels="labels"
              :data="dailyPortfolio"
              :smooth="true"
              :areaStyle="true"
            />

              <!-- Asset Allocation -->
              <PortfolioAssetAllocation :allocation-data="activePortfolio?.allocationData" />

              <!-- Holdings List -->
              <div class="bg-white dark:bg-gray-800 rounded-xl shadow p-4">
                <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Holdings</h2>
                <div class="space-y-2">
                  <div 
                    v-for="holding in activePortfolio.holdings" 
                    :key="holding.ticker"
                    class="flex items-center justify-between p-2 rounded hover:bg-gray-100 dark:hover:bg-gray-700"
                  >
                    <!-- Left: Icon + Name -->
                    <div class="flex items-center gap-3">
                      <div class="w-8 h-8 rounded-full bg-gray-300 dark:bg-gray-600 flex items-center justify-center text-sm font-bold text-white">
                        {{ holding.ticker[0] }}
                      </div>
                      <div>
                        <div class="font-semibold text-gray-900 dark:text-white">{{ holding.ticker }}</div>
                        <div class="text-sm text-gray-500 dark:text-gray-400">{{ holding.company }}</div>
                      </div>
                    </div>

                    <!-- Middle: Shares + Gains -->
                    <div class="text-right">
                      <div>{{ holding.shares }} shares</div>
                      <div :class="holding.gain >= 0 ? 'text-green-500' : 'text-red-500'">
                        {{ formatCurrency(holding.gain) }} ({{ holding.gainPerc }}%)
                      </div>
                    </div>

                    <!-- Right: Allocation Bar -->
                    <div class="w-40 flex flex-col items-end">
                      <div class="w-full bg-gray-200 dark:bg-gray-700 h-2 rounded">
                        <div class="h-2 rounded bg-indigo-500" :style="{ width: holding.allocation + '%' }"></div>
                      </div>
                      <div class="text-sm text-gray-500 dark:text-gray-400 mt-1">{{ holding.allocation }}%</div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Transactions Table -->
              <div class="space-y-2">
                <div class="flex justify-end">
                  <button class="px-3 py-2 bg-indigo-500 text-white rounded hover:bg-indigo-600">
                    + Add Transaction
                  </button>
                </div>
                <TailwindDataTable
                  :columns="transactionColumns"
                  :data="activePortfolio?.transactions || []"
                />
              </div>

            </div>

            <!-- Dividends Tab -->
            <div v-if="activeTab === 'Dividends'" class="grid md:grid-cols-2 gap-4">
              <div class="bg-gray-100 dark:bg-gray-700 rounded h-[200px] flex items-center justify-center">
                Past Dividends Chart
              </div>
              <div class="bg-gray-100 dark:bg-gray-700 rounded h-[200px] flex items-center justify-center">
                Dividend Calendar
              </div>
            </div>

            <!-- Analysis Tab -->
            <div v-if="activeTab === 'Analysis'" class="space-y-4">
              <div class="bg-gray-100 dark:bg-gray-700 rounded h-[250px] flex items-center justify-center">
                Portfolio Analysis Placeholder
              </div>
            </div>

            <!-- News Tab -->
            <div v-if="activeTab === 'News'" class="space-y-4">
              <div class="bg-gray-100 dark:bg-gray-700 rounded h-[250px] flex items-center justify-center">
                News Feed Placeholder
              </div>
            </div>

          </div>
        </div>

      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { PlusIcon } from '@heroicons/vue/24/outline'
import SectionTitle from '@/components/subcomponents/SectionTitle.vue'
import PortfolioKpiCards from "@/components/proto/PortfolioKpiCards.vue"
import TailwindDataTable from '@/components/tables/TailwindDataTable.vue'
import PortfolioAssetAllocation from "@/components/proto/PortfolioAssetAllocation.vue"
import PortfolioPerformanceChart from "@/components/proto/PortfolioPerformanceChart.vue"


const portfolios = reactive([
  { 
    name: 'Tech Portfolio',
    currentValue: '€ 120,450',
    totalGain: '+15.2%',
    invested: '€ 100,000',
    dividends: '€ 2,340',
    realized: '€ 5,100',
    izf: '7.5%',
    transactions: [
      { ticker: 'AAPL', type: 'Buy', shares: 10, value: '€ 1,500' },
      { ticker: 'MSFT', type: 'Sell', shares: 5, value: '€ 1,200' }
    ],
    holdings: [
      { ticker: 'AAPL', company: 'Apple Inc.', shares: 50, gain: 1200, gainPerc: 10, allocation: 30 },
      { ticker: 'MSFT', company: 'Microsoft Corp.', shares: 30, gain: 800, gainPerc: 8, allocation: 25 },
      { ticker: 'AMZN', company: 'Amazon.com Inc.', shares: 20, gain: -300, gainPerc: -5, allocation: 20 },
      { ticker: 'TSLA', company: 'Tesla Inc.', shares: 10, gain: 500, gainPerc: 12, allocation: 25 }
    ],
    performanceData: [100000, 102000, 105000, 120450],
    allocationData: [
      { value: 80, name: 'Stocks' },
      { value: 20, name: 'Cash' }
    ]
  }
])

const activeIndex = ref(0)
const activePortfolio = computed(() => portfolios[activeIndex.value])

const activeTab = ref('Overview')
const tabs = ['Overview', 'Dividends', 'Analysis', 'News']

const transactionColumns = [
  { name: 'Ticker', key: 'ticker' },
  { name: 'Type', key: 'type' },
  { name: 'Shares', key: 'shares' },
  { name: 'Value', key: 'value' }
]

function selectPortfolio(index) {
  activeIndex.value = index
}

const formatCurrency = (value) => {
  return new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(value)
}

//Create mock data for portfolio performance
function generateDailyPortfolioData(startValue = 100000, days = 252, volatility = 0.02) {
  const data = [startValue]
  for (let i = 1; i < days; i++) {
    const change = (Math.random() * 2 - 1) * volatility
    data.push(Math.round(data[i-1] * (1 + change)))
  }
  return data
}

const dailyPortfolio = generateDailyPortfolioData()
const labels = dailyPortfolio.map((_, i) => `Day ${i+1}`)
</script>
