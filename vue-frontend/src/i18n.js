import { createI18n } from 'vue-i18n'
import { nextTick } from 'vue'

const INIT_LANGUAGE = 'en'
export const SUPPORTED_LOCALES = ['en', 'de']

// create a singleton i18n instance here
export const i18n = createI18n({
  legacy: false,
  locale: INIT_LANGUAGE,
  fallbackLocale: INIT_LANGUAGE,
  messages: {}, // start empty
})

export function setI18nLanguage(i18nInstance, locale) {
  if (i18nInstance.mode === 'legacy') {
    i18nInstance.global.locale = locale
  } else {
    i18nInstance.global.locale.value = locale
  }
  document.querySelector('html').setAttribute('lang', locale)
}

export async function loadLocaleMessages(i18nInstance, locale) {
  const stocks = await import(`./locales/${locale}/stocks.json`)

  i18nInstance.global.setLocaleMessage(locale, {
    stocks: stocks.default,
  })

  return nextTick()
}
