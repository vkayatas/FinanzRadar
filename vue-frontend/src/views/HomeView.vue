<!-- src/views/HomeView.vue -->
<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-white">
    <!-- Hero Section -->
    <section class="relative bg-gradient-to-r from-indigo-600 to-purple-600 text-white">
      <div class="container mx-auto px-6 py-24 text-center">
        <h1 class="text-5xl font-extrabold sm:text-6xl lg:text-7xl drop-shadow-lg">
          Track Stocks & Portfolios <span class="text-indigo-300">Effortlessly</span>
        </h1>
        <p class="mt-6 text-lg sm:text-xl max-w-xl mx-auto drop-shadow-md">
          Analyze fundamentals, monitor your watchlist, and follow your portfolios' growth — all in one dashboard.
        </p>
        <router-link
          to="/stock-analysis"
          class="mt-8 inline-block px-8 py-4 bg-white text-indigo-700 font-semibold rounded-xl shadow-lg hover:scale-105 transition transform"
        >
          Get Started
        </router-link>
      </div>
    </section>

    <!-- Features Cards Section -->
    <section class="container mx-auto px-6 py-20">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
        <!-- Stock Analysis Card -->
        <div class="bg-white dark:bg-gray-800 rounded-3xl shadow-xl hover:shadow-2xl transform hover:-translate-y-2 transition p-8">
          <div class="flex items-center justify-center h-16 w-16 rounded-full bg-gradient-to-r from-indigo-500 to-purple-500 text-white text-2xl font-bold mb-6">
            📈
          </div>
          <h2 class="text-2xl font-bold mb-2">Stock Analysis</h2>
          <p class="text-gray-600 dark:text-gray-300 mb-4">
            Search ticker symbols, view financial charts, revenue, margins, earnings, and more.
          </p>
          <router-link
            to="/stock-analysis"
            class="inline-block px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition"
          >
            Explore
          </router-link>
        </div>

        <!-- Watchlist Card -->
        <div class="bg-white dark:bg-gray-800 rounded-3xl shadow-xl hover:shadow-2xl transform hover:-translate-y-2 transition p-8">
          <div class="flex items-center justify-center h-16 w-16 rounded-full bg-gradient-to-r from-green-500 to-teal-500 text-white text-2xl font-bold mb-6">
            ⭐
          </div>
          <h2 class="text-2xl font-bold mb-2">Watchlist</h2>
          <p class="text-gray-600 dark:text-gray-300 mb-4">
            Track your favorite stocks, see price dips, and follow upcoming earnings calls.
          </p>
          <router-link
            to="/watchlist"
            class="inline-block px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition"
          >
            View
          </router-link>
        </div>

        <!-- Portfolio Card -->
        <div class="bg-white dark:bg-gray-800 rounded-3xl shadow-xl hover:shadow-2xl transform hover:-translate-y-2 transition p-8">
          <div class="flex items-center justify-center h-16 w-16 rounded-full bg-gradient-to-r from-yellow-500 to-orange-500 text-white text-2xl font-bold mb-6">
            💰
          </div>
          <h2 class="text-2xl font-bold mb-2">Portfolio</h2>
          <p class="text-gray-600 dark:text-gray-300 mb-4">
            Track multiple portfolios, monitor growth over time, and analyze performance metrics.
          </p>
          <router-link
            to="/portfolio"
            class="inline-block px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 transition"
          >
            Manage
          </router-link>
        </div>
      </div>
    </section>

    <!-- Call to Action Section -->
    <section class="bg-indigo-50 dark:bg-gray-800 text-center py-20">
      <h2 class="text-4xl font-bold mb-4">Start investing smarter today</h2>
      <p class="text-gray-700 dark:text-gray-300 max-w-2xl mx-auto mb-8">
        Join thousands of users tracking their stocks and portfolios effortlessly.
      </p>
      <router-link
        to="/stock-analysis"
        class="px-10 py-4 bg-indigo-600 text-white rounded-xl font-semibold shadow-lg hover:bg-indigo-700 hover:scale-105 transition transform"
      >
        Get Started
      </router-link>
    </section>
  </div>
</template>

<script setup>
// No logic for now, all routing is handled by Vue Router
</script>

<style scoped>
/* Optional: add smooth gradient background animations or small hover effects if desired */
</style>
