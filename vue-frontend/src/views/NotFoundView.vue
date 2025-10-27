<!-- src/views/NotFoundView.vue -->
<template>
  <div class="flex items-center justify-center min-h-screen bg-gray-50 dark:bg-gray-900">
    <div class="text-center px-6 py-12">
      <h1 class="text-6xl font-extrabold text-gray-900 dark:text-white mb-4">404</h1>
      <p class="text-xl text-gray-700 dark:text-gray-300 mb-6">
        Oops! The page you are looking for does not exist.
      </p>
      <router-link to="/" class="inline-block px-6 py-3 bg-indigo-600 text-white font-semibold rounded-lg hover:bg-indigo-700 transition-colors">
        Go Back Home
      </router-link>
    </div>
  </div>
</template>

