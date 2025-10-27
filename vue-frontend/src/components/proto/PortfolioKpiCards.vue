<template>
  <section class="grid grid-cols-2 md:grid-cols-4 gap-4">
    <KpiCard title="Current Value" :value="portfolio?.currentValue || '€ 0'" />
    <KpiCard title="Total Gain/Loss" :value="portfolio?.totalGain || '0%'" />
    <KpiCard title="Invested Capital" :value="portfolio?.invested || '€ 0'" />
    <KpiCard title="Dividends" :value="portfolio?.dividends || '€ 0'" />
    <KpiCard title="Realized Gains" :value="portfolio?.realized || '€ 0'" />
    <KpiCard title="IZF (IRR)" :value="portfolio?.izf || '0%'" />
  </section>
</template>

<script setup>
import KpiCard from '@/components/subcomponents/KpiCard.vue'
defineProps({ portfolio: Object })
</script>
