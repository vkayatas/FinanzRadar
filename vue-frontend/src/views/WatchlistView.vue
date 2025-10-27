<template>
  <!-- Feature 1: Header -->
  <div class="row-start-1 text-center mb-6">
    <h1 class="text-3xl font-bold text-gray-900 dark:text-white">Watchlist</h1>
    <p class="text-gray-600 dark:text-gray-300 mt-4">
      Track your favorite stocks, follow upcoming earnings reports and spot market dips at a glance.
    </p>
  </div>

  <div class="grid grid-cols-1 lg:grid-cols-12 gap-4 lg:gap-6 items-start bg-gray-50 dark:bg-gray-900">
    <!-- Sidebar -->
    <aside class="bg-white dark:bg-gray-800 rounded-xl shadow-md p-3 flex flex-col lg:sticky top-4 lg:col-span-3">
      
      <SectionTitle title="Your Watchlists" />

      <!-- Scrollable Watchlist Items -->
      <div class="mt-2 flex-1 overflow-y-auto space-y-2 pr-1">
        <div 
          v-for="(watchlist, index) in store.watchlists" 
          :key="index"
          class="flex items-center justify-between p-2 rounded hover:bg-gray-100 dark:hover:bg-gray-700 cursor-pointer"
          @click="selectWatchlist(index)"
          :class="store.activeWatchlist === watchlist ? 'bg-gray-200 dark:bg-gray-700 font-semibold' : ''"
        >
          <span>{{ watchlist.name }} ({{ watchlist.stocks.length }})</span>
          <TrashIcon 
            class="w-5 h-5 text-red-500 hover:text-red-600"
            @click.stop="openDeleteDialog(index)"
          />
        </div>
      </div>

      <!-- Button always at bottom -->
      <div class="mt-4 pt-2 border-t border-gray-200 dark:border-gray-700">
        <button 
          class="w-full flex items-center justify-center gap-2 px-3 py-2 bg-indigo-500 text-white rounded hover:bg-indigo-600"
          @click="newWatchlistOpen = true"
        >
          <PlusIcon class="w-5 h-5" />
          New Watchlist
        </button>
      </div>

    </aside>

    <!-- Main content -->
    <main class="flex flex-col gap-4 lg:col-span-9">

      <!-- Watchlist Table -->
      <section class="bg-white dark:bg-gray-800 rounded-xl shadow p-4">
        <SectionTitle :title="store.activeWatchlist?.name || 'No Watchlist Selected'" />
        <div v-if="store.activeWatchlist">
          <PrimevueDataTableAnnotation
            :columns="store.watchlistColumns"
            :data="store.activeWatchlist?.stocks || []"
            @add="openAddDialog"
            @remove="removeStockWatchlist"
          />
        </div>
        <div v-else class="text-gray-500 dark:text-gray-400 text-center py-10">
          Select or create a watchlist to see stocks.
        </div>
      </section>

      <!-- Upcoming Earnings Section -->
      <section v-if="store.activeWatchlist" class="bg-white dark:bg-gray-800 rounded-xl shadow p-4">
        <SectionTitle title="Upcoming Earnings" />
        <PrimevueDataTable
          :columns="store.earningsColumns"
          :data="store.activeWatchlist?.upcomingEarnings || []"
        />
      </section>

      <!-- Dip Finder -->
      <section v-if="store.activeWatchlist" class="bg-white dark:bg-gray-800 rounded-xl shadow p-4">
        <SectionTitle title="Dip Finder" />
        <DipFinderChart :dip-data="store.activeWatchlist?.dipData || {}" />
      </section>

      <!-- Watchlist Fundamentals Section -->
      <section v-if="store.activeWatchlist" class="bg-white dark:bg-gray-800 rounded-xl shadow p-4">
        <SectionTitle title="Watchlist Fundamentals" />
        <PrimevueDataTable
          :columns="store.fundamentalsColumns"
          :data="store.activeWatchlist?.fundamentals || []"
        />
      </section>
    </main>

    <!-- Delete Confirmation Dialog -->
    <TransitionRoot as="template" :show="deleteDialogOpen">
      <Dialog as="div" class="relative z-50" @close="deleteDialogOpen = false">
        <div class="fixed inset-0 bg-black/20 backdrop-blur-sm pointer-events-auto"></div>
        <div class="fixed inset-0 flex items-center justify-center p-4 pointer-events-none">
          <TransitionChild
            enter="transition ease-out duration-150"
            enter-from="opacity-0 scale-95"
            enter-to="opacity-100 scale-100"
            leave="transition ease-in duration-100"
            leave-from="opacity-100 scale-100"
            leave-to="opacity-0 scale-95"
          >
            <DialogPanel class="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 w-full max-w-lg pointer-events-auto">
              <DialogTitle class="text-lg font-semibold text-gray-900 dark:text-gray-100">
                Delete Watchlist
              </DialogTitle>
              <DialogDescription class="mt-2 text-gray-700 dark:text-gray-300">
                Are you sure you want to delete "{{ store.watchlists[deleteIndex]?.name }}"? 
                It currently has {{ store.watchlists[deleteIndex]?.stocks.length || 0 }} stocks.
              </DialogDescription>
              <div class="mt-4 flex justify-end gap-2">
                <button
                  class="px-4 py-2 rounded bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600"
                  @click="deleteDialogOpen = false"
                >Cancel</button>
                <button
                  class="px-4 py-2 rounded bg-red-500 text-white hover:bg-red-600"
                  @click="deleteWatchlist"
                >Delete</button>
              </div>
            </DialogPanel>
          </TransitionChild>
        </div>
      </Dialog>
    </TransitionRoot>

    <!-- New Watchlist Dialog -->
    <TransitionRoot as="template" :show="newWatchlistOpen">
      <Dialog as="div" class="relative z-50" @close="newWatchlistOpen = false">
        <div class="fixed inset-0 bg-black/20 backdrop-blur-sm pointer-events-auto"></div>
        <div class="fixed inset-0 flex items-center justify-center p-4 pointer-events-none">
          <TransitionChild
            enter="transition ease-out duration-150"
            enter-from="opacity-0 scale-95"
            enter-to="opacity-100 scale-100"
            leave="transition ease-in duration-100"
            leave-from="opacity-100 scale-100"
            leave-to="opacity-0 scale-95"
          >
            <DialogPanel class="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 w-xs sm:w-lg pointer-events-auto">
              <DialogTitle class="text-lg font-semibold text-gray-900 dark:text-gray-100">
                Create New Watchlist
              </DialogTitle>
              <div class="mt-2">
                <input
                  v-model="newWatchlistName"
                  placeholder="Watchlist Name"
                  class="w-full border border-gray-300 dark:border-gray-600 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500 dark:bg-gray-700 dark:text-white"
                  @keydown.enter.prevent="createWatchlist"
                />
              </div>
              <div class="mt-4 flex justify-end gap-2">
                <button
                  class="px-4 py-2 rounded bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600"
                  @click="newWatchlistOpen = false"
                >Cancel</button>
                <button
                  class="px-4 py-2 rounded bg-indigo-500 text-white hover:bg-indigo-600"
                  @click="createWatchlist"
                >Create</button>
              </div>
            </DialogPanel>
          </TransitionChild>
        </div>
      </Dialog>
    </TransitionRoot>

    <!-- Add Stock Dialog -->
    <WatchlistAddStockDialog
      v-model="addDialog"
      :activeWatchlist="store.activeWatchlist"
      @add="addStockWatchlist"
    />
  </div>
</template>

<script setup>
import SectionTitle from '@/components/subcomponents/SectionTitle.vue'
import DipFinderChart from '@/components/charts/DipFinderChart.vue'
import PrimevueDataTable from '@/components/tables/PrimevueDataTable.vue'
import PrimevueDataTableAnnotation from '@/components/tables/PrimevueDataTableAnnotation.vue'
import WatchlistAddStockDialog from '@/components/ui/WatchlistAddStockDialog.vue'

import { Dialog, DialogPanel, DialogTitle, DialogDescription, TransitionRoot, TransitionChild } from '@headlessui/vue'
import { TrashIcon, PlusIcon } from '@heroicons/vue/24/outline'
import { ref } from 'vue'
import { useWatchlistStore } from '@/stores/watchlistStore'

// ---- STORE ----
const store = useWatchlistStore()

// ---- DIALOG STATE ----
const deleteDialogOpen = ref(false)
const deleteIndex = ref(null)
const newWatchlistOpen = ref(false)
const newWatchlistName = ref('')
const addDialog = ref(false)

// ---- FUNCTIONS ----
function selectWatchlist(index) {
  store.selectWatchlist(index)
}

function openDeleteDialog(index) {
  deleteIndex.value = index
  deleteDialogOpen.value = true
}

function deleteWatchlist() {
  if (deleteIndex.value !== null) {
    store.deleteWatchlist(deleteIndex.value)
    deleteDialogOpen.value = false
  }
}

function createWatchlist() {
  if (newWatchlistName.value.trim()) {
    store.createWatchlist(newWatchlistName.value)
    newWatchlistName.value = ''
    newWatchlistOpen.value = false
  }
}

function openAddDialog() {
  addDialog.value = true
}

function addStockWatchlist({ stock }) {
  store.addStock(stock)
}

function removeStockWatchlist(stock) {
  store.removeStock(stock)
}
</script>
