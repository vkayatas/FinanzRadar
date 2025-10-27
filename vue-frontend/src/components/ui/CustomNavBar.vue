<template>
  <Disclosure as="nav" class="relative bg-gray-800 dark:bg-gray-800 z-50" v-slot="{ open }">
    <div class="mx-auto max-w-7xl px-2 md:px-6 lg:px-8">
      <div class="relative flex h-16 items-center justify-between">

        <!-- Mobile menu button -->
        <div class="absolute inset-y-0 left-0 flex items-center lg:hidden">
          <DisclosureButton class="relative inline-flex items-center justify-center rounded-md p-2 text-gray-400 hover:bg-white/5 hover:text-white focus:outline-2 focus:-outline-offset-1 focus:outline-indigo-500">
            <span class="sr-only">Open main menu</span>
            <Bars3Icon v-if="!open" class="block size-6" aria-hidden="true" />
            <XMarkIcon v-else class="block size-6" aria-hidden="true" />
          </DisclosureButton>
        </div>

        <!-- Logo & desktop menu -->
        <div class="flex flex-1 items-center justify-center lg:items-stretch lg:justify-start">
          <router-link to="/" class="flex shrink-0 items-center space-x-2">
            <img class="h-8 w-auto" src="https://tailwindcss.com/plus-assets/img/logos/mark.svg?color=indigo&shade=500" alt="Logo" />
            <span class="text-white font-bold text-xl">{{ appName }}</span>
          </router-link>

          <div class="hidden lg:ml-6 lg:block">
            <div class="flex space-x-4">
              <router-link
                v-for="item in navigation"
                :key="item.name"
                :to="item.href"
                class="rounded-md px-3 py-2 text-sm font-medium"
                :class="isActive(item.href) ? 'bg-gray-900 text-white dark:bg-gray-950/50' : 'text-gray-300 hover:bg-white/5 hover:text-white'"
              >
                {{ item.name }}
              </router-link>
            </div>
          </div>
        </div>

        <!-- Right side: notifications, profile, language selector -->
        <div class="absolute inset-y-0 right-0 flex items-center pr-2 lg:static lg:inset-auto lg:ml-6 lg:pr-0 space-x-4">

          <!-- Language dropdown -->
          <select
            v-model="userStore.language"
            @change="changeLanguage"
            class="rounded-md hidden sm:block bg-gray-700 text-white px-2 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            <option v-for="lang in userStore.supportedLanguages" :key="lang" :value="lang">
              {{ lang.toUpperCase() }}
            </option>
          </select>

          <!-- Notifications -->
          <button type="button" class="relative rounded-full p-1 text-gray-400 focus:outline-2 focus:outline-offset-2 focus:outline-indigo-500 dark:hover:text-white">
            <span class="sr-only">View notifications</span>
            <BellIcon class="size-6" aria-hidden="true" />
          </button>

          <!-- Profile menu -->
          <Menu as="div" class="relative ml-3">
            <MenuButton class="relative flex rounded-full focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-500">
              <span class="sr-only">Open user menu</span>
              <img class="size-8 rounded-full bg-gray-800 outline -outline-offset-1 outline-white/10" 
                   src="https://images.unsplash.com/photo-1472099645785-5658abf4ff4e" alt="User" />
            </MenuButton>

            <transition enter-active-class="transition ease-out duration-100" enter-from-class="transform opacity-0 scale-95" enter-to-class="transform scale-100"
                        leave-active-class="transition ease-in duration-75" leave-from-class="transform scale-100" leave-to-class="transform opacity-0 scale-95">
              <MenuItems class="absolute right-0 z-10 mt-2 w-48 origin-top-right rounded-md bg-white py-1 shadow-lg outline outline-black/5 dark:bg-gray-800 dark:shadow-none dark:-outline-offset-1 dark:outline-white/10">
                <MenuItem v-slot="{ active }">
                  <a href="#" :class="[active ? 'bg-gray-100 dark:bg-white/5' : '', 'block px-4 py-2 text-sm text-gray-700 dark:text-gray-300']">Your profile</a>
                </MenuItem>
                <MenuItem v-slot="{ active }">
                  <a href="#" :class="[active ? 'bg-gray-100 dark:bg-white/5' : '', 'block px-4 py-2 text-sm text-gray-700 dark:text-gray-300']">Settings</a>
                </MenuItem>
                <MenuItem v-slot="{ active }">
                  <a href="#" :class="[active ? 'bg-gray-100 dark:bg-white/5' : '', 'block px-4 py-2 text-sm text-gray-700 dark:text-gray-300']">Sign out</a>
                </MenuItem>
              </MenuItems>
            </transition>
          </Menu>
        </div>
      </div>
    </div>

    <!-- Mobile menu -->
    <DisclosurePanel class="lg:hidden">
      <div class="space-y-1 px-2 pt-2 pb-3">
        <router-link
          v-for="item in navigation"
          :key="item.name"
          :to="item.href"
          class="block rounded-md px-3 py-2 text-base font-medium"
          :class="isActive(item.href) ? 'bg-gray-900 text-white dark:bg-gray-950/50' : 'text-gray-300 hover:bg-white/5 hover:text-white'"
        >
          {{ item.name }}
        </router-link>
      </div>
    </DisclosurePanel>
  </Disclosure>
</template>

<script setup>
import { Disclosure, DisclosureButton, DisclosurePanel, Menu, MenuButton, MenuItem, MenuItems } from '@headlessui/vue'
import { Bars3Icon, BellIcon, XMarkIcon } from '@heroicons/vue/24/outline'
import { useRoute } from 'vue-router'
import { APP_NAME } from '@/config/index.js'
import { useUserStore } from '@/stores/userStore'
import { i18n, loadLocaleMessages, setI18nLanguage } from '@/i18n'

const appName = APP_NAME
const route = useRoute()
const navigation = [
  { name: 'StockAnalysis', href: '/stock-analysis' },
  { name: 'Watchlist', href: '/watchlist' },
  { name: 'Portfolio', href: '/portfolio' },
  { name: 'About', href: '/about' },
  { name: 'Prototyping', href: '/prototyping' },
]

const isActive = (href) => route.path === href

// Pinia store
const userStore = useUserStore()

// Change language
async function changeLanguage() {
  await userStore.setLanguage(userStore.language, i18n)
}
</script>
