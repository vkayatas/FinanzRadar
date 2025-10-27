<!-- src/App.vue -->
<template>
  <div id="app" class="min-h-screen flex flex-col bg-gray-50 dark:bg-gray-900 transition-colors duration-300">
    <!-- Navbar -->
    <CustomNavBar />

    <!-- Main content -->
    <main class="flex-1 w-full mx-auto px-4 sm:px-6 lg:px-12 py-6 overflow-x-hidden">
      <router-view class="block w-full" />
    </main>

    <!-- Footer -->
    <footer class="bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 py-4 text-center text-sm border-t border-gray-200 dark:border-gray-700">
      © {{ year }} {{ appName }}
    </footer>
  </div>
</template>

<script setup>
import CustomNavBar from '@/components/ui/CustomNavBar.vue'
import { APP_NAME, CURRENT_YEAR } from './config/index.js'

const appName = APP_NAME
const year = CURRENT_YEAR
</script>
