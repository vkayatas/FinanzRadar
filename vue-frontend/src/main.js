import App from './App.vue'
import { createApp } from 'vue'
import { router } from './router';
import { createPinia } from 'pinia'
import { VueQueryPlugin, QueryClient } from '@tanstack/vue-query';
import '@/styles/globals.css';
import { vueQueryOptions } from '@/config/caching';
import { useUserStore } from '@/stores/userStore'

// Init app
const app = createApp(App);

// Install plugins:
// 1) Pinia store
const pinia = createPinia();
app.use(pinia);
const userStore = useUserStore()

// 2) Router
app.use(router);

// 3) VueQuery
const queryClient = new QueryClient({ defaultOptions: vueQueryOptions });
app.use(VueQueryPlugin, { queryClient });

// 4) Language selection
import { i18n, loadLocaleMessages  } from './i18n'
app.use(i18n)
await loadLocaleMessages(i18n, userStore.language)

// 5) PrimeVue datatable
import PrimeVue from 'primevue/config'
import Aura from '@primeuix/themes/aura';
app.use(PrimeVue, {
    theme: {
        preset: Aura
    }
});

//  Mount app 
app.mount('#app');