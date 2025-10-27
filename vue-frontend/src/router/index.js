import { createRouter, createWebHistory } from 'vue-router';

const routes = [
  { path: '/', name: 'Home', component: () => import('@/views/HomeView.vue') },
  { path: '/about', name: 'About', component: () => import('@/views/AboutView.vue') },
  { path: '/stock-analysis', name: 'StockAnalysis', component: () => import('@/views/StockAnalysisView.vue') },
  { path: '/watchlist', name: 'Watchlist', component: () => import('@/views/WatchlistView.vue') },
  { path: '/portfolio', name: 'Portfolio', component: () => import('@/views/PortfolioView.vue') },
  { path: '/prototyping', name: 'Prototyping', component: () => import('@/views/PrototypingView.vue') },
  { path: '/:pathMatch(.*)*', name: 'NotFound', component: () => import('@/views/NotFoundView.vue') },
];

export const router = createRouter({
  history: createWebHistory(),
  routes,
});
