import { defineStore } from 'pinia'
import { loadLocaleMessages, i18n } from '../i18n'

export const useUserStore = defineStore('userSettings', {
  state: () => ({
    language: 'en', // current language
    supportedLanguages: ['en', 'de'],
    currency: '$', // current currency symbol
    supportedCurrencies: ['$', '€'], 
  }),
  actions: {
    async setLanguage(newLocale) {
      if (!this.supportedLanguages.includes(newLocale)) {
        console.warn(`Locale ${newLocale} not supported, falling back to 'en'`)
        newLocale = 'en'
      }

      // lazy load locale messages if needed
      if (!i18n.global.availableLocales.includes(newLocale)) {
        await loadLocaleMessages(i18n, newLocale)
      }

      this.language = newLocale
      i18n.global.locale.value = newLocale
      document.querySelector('html').setAttribute('lang', newLocale)
    }
  }
})
