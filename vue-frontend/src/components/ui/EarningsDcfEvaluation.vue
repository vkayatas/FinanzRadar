<template>
    <div class="bg-white dark:bg-gray-800 p-4 rounded-lg shadow overflow-x-auto">
        <!-- Row 1: Title -->
        <h2 class="text-base sm:text-xl font-bold mb-4 border-b-4 border-indigo-500 dark:border-indigo-400 inline-block pb-1">
            DCF Evaluation
        </h2>

        <!-- Row 2: DCF Mode Toggle -->
        <div class="mb-6">
            <div class="flex flex-wrap items-center gap-3">
                <label
                    class="flex items-center justify-center px-4 py-2 border rounded-lg cursor-pointer transition-all hover:bg-indigo-50 dark:hover:bg-indigo-900"
                    :class="dcfMode === 'EPS' 
            ? 'bg-indigo-100 border-indigo-500 text-indigo-700 dark:bg-indigo-800 dark:text-indigo-200' 
            : 'bg-white border-gray-300 dark:bg-gray-700 dark:text-gray-300'"
                >
                    <input type="radio" value="EPS" v-model="dcfMode" class="hidden" />
                    <span class="font-medium">EPS-Based DCF</span>
                </label>

                <label
                    class="flex items-center justify-center px-4 py-2 border rounded-lg cursor-pointer transition-all hover:bg-indigo-50 dark:hover:bg-indigo-900"
                    :class="dcfMode === 'FCF' 
            ? 'bg-indigo-100 border-indigo-500 text-indigo-700 dark:bg-indigo-800 dark:text-indigo-200' 
            : 'bg-white border-gray-300 dark:bg-gray-700 dark:text-gray-300'"
                >
                    <input type="radio" value="FCF" v-model="dcfMode" class="hidden" />
                    <span class="font-medium">FCF-Based DCF</span>
                </label>
            </div>
        </div>

        <!-- Row 3: Grid layout -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <!-- Left Column: Assumptions -->
            <div class="space-y-6 lg:col-span-1">
                <h3 class="text-lg font-semibold mb-2 border-b border-gray-300 dark:border-gray-600 pb-1">Assumptions</h3>

                <!-- Card: Hard Facts -->
                <div class="p-6 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 rounded-lg">
                    <h4 class="text-sm font-semibold mb-4 text-gray-700 dark:text-gray-200 tracking-wide">Fundamentals</h4>

                    <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4 text-sm">
                        <div class="flex justify-between items-center p-3 rounded-xl bg-white dark:bg-gray-700 shadow-sm border border-gray-100 dark:border-gray-600">
                            <span class="text-gray-500 dark:text-gray-300">Ticker:</span>
                            <span class="font-semibold text-gray-900 dark:text-gray-100">{{ hardFacts.ticker }}</span>
                        </div>

                        <div v-if="dcfMode === 'FCF'" class="flex justify-between items-center p-3 rounded-xl bg-white dark:bg-gray-700 shadow-sm border border-gray-100 dark:border-gray-600">
                            <span class="text-gray-500 dark:text-gray-300">Last Year FCF:</span>
                            <span class="font-semibold text-gray-900 dark:text-gray-100">${{ hardFacts.lastFCF.toLocaleString() }}</span>
                        </div>

                        <div v-if="dcfMode === 'EPS'" class="flex justify-between items-center p-3 rounded-xl bg-white dark:bg-gray-700 shadow-sm border border-gray-100 dark:border-gray-600">
                            <span class="text-gray-500 dark:text-gray-300">EPS (TTM):</span>
                            <span class="font-semibold text-gray-900 dark:text-gray-100">${{ lastEPS.toFixed(2) }}</span>
                        </div>

                        <div class="flex justify-between items-center p-3 rounded-xl bg-white dark:bg-gray-700 shadow-sm border border-gray-100 dark:border-gray-600">
                            <span class="text-gray-500 dark:text-gray-300">Cash:</span>
                            <span class="font-semibold text-gray-900 dark:text-gray-100">${{ hardFacts.cash.toLocaleString() }}</span>
                        </div>

                        <div class="flex justify-between items-center p-3 rounded-xl bg-white dark:bg-gray-700 shadow-sm border border-gray-100 dark:border-gray-600">
                            <span class="text-gray-500 dark:text-gray-300">Debt:</span>
                            <span class="font-semibold text-gray-900 dark:text-gray-100">${{ hardFacts.debt.toLocaleString() }}</span>
                        </div>

                        <div class="flex justify-between items-center p-3 rounded-xl bg-white dark:bg-gray-700 shadow-sm border border-gray-100 dark:border-gray-600">
                            <span class="text-gray-500 dark:text-gray-300">Shares Outstanding:</span>
                            <span class="font-semibold text-gray-900 dark:text-gray-100">{{ hardFacts.sharesOutstanding.toLocaleString() }}</span>
                        </div>
                    </div>
                </div>

                <!-- Card: Current Cash Flow / Earnings -->
                <div class="p-6 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 rounded-lg">
                    <h5 class="text-sm font-semibold mb-4 text-gray-700 dark:text-gray-200 tracking-wide">
                        {{ dcfMode === 'EPS' ? 'Current Earnings (TTM)' : 'Current Cash Flow (TTM)' }}
                    </h5>

                    <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 text-sm">
                        <div v-if="dcfMode === 'FCF'" class="flex justify-between items-center p-3 rounded-xl bg-white dark:bg-gray-700 shadow-sm border border-gray-100 dark:border-gray-600">
                            <span class="text-gray-500 dark:text-gray-300">FCF/Share:</span>
                            <span class="font-semibold text-gray-900 dark:text-gray-100">${{ fcfPerShare.toFixed(2) }}</span>
                        </div>

                        <div v-if="dcfMode === 'EPS'" class="flex justify-between items-center p-3 rounded-xl bg-white dark:bg-gray-700 shadow-sm border border-gray-100 dark:border-gray-600">
                            <span class="text-gray-500 dark:text-gray-300">EPS (TTM):</span>
                            <span class="font-semibold text-gray-900 dark:text-gray-100">{{ lastEPS.toFixed(2) }}</span>
                        </div>

                        <div v-if="dcfMode === 'FCF'" class="flex justify-between items-center p-3 rounded-xl bg-white dark:bg-gray-700 shadow-sm border border-gray-100 dark:border-gray-600">
                            <span class="text-gray-500 dark:text-gray-300">FCF Yield:</span>
                            <span class="font-semibold text-gray-900 dark:text-gray-100">{{ (fcfYield * 100).toFixed(2) }}%</span>
                        </div>

                        <div v-if="dcfMode === 'EPS'" class="flex justify-between items-center p-3 rounded-xl bg-white dark:bg-gray-700 shadow-sm border border-gray-100 dark:border-gray-600">
                            <span class="text-gray-500 dark:text-gray-300">PE Ratio:</span>
                            <span class="font-semibold text-gray-900 dark:text-gray-100">{{ peRatio.toFixed(2) }}</span>
                        </div>

                        <div v-if="dcfMode === 'EPS'" class="flex justify-between items-center p-3 rounded-xl bg-white dark:bg-gray-700 shadow-sm border border-gray-100 dark:border-gray-600">
                            <span class="text-gray-500 dark:text-gray-300">EPS Growth:</span>
                            <span class="font-semibold text-gray-900 dark:text-gray-100">{{ dcfParams.epsGrowth }}%</span>
                        </div>

                        <div v-if="dcfMode === 'FCF'" class="flex justify-between items-center p-3 rounded-xl bg-white dark:bg-gray-700 shadow-sm border border-gray-100 dark:border-gray-600">
                            <span class="text-gray-500 dark:text-gray-300">SBC Impact:</span>
                            <span class="font-semibold text-gray-900 dark:text-gray-100">${{ sbcImpact.toLocaleString() }}</span>
                        </div>
                    </div>
                </div>

                <!-- Card: Assumption Inputs -->
                <div class="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg border border-gray-100 dark:border-gray-600 space-y-4">
                    <!-- Non-editable Share Value -->
                    <div class="flex items-center gap-4">
                        <label class="w-48 text-sm font-medium text-gray-900 dark:text-gray-200 text-left">
                            {{ dcfMode === 'EPS' ? 'EPS (TTM)' : 'FCF/Share (TTM)' }}:
                        </label>
                        <div class="flex items-stretch flex-1 rounded-md ring-1 ring-gray-200 dark:ring-gray-700 bg-white dark:bg-gray-800 overflow-hidden focus-within:ring-indigo-500">
                            <input
                                type="text"
                                :value="dcfMode === 'EPS' ? lastEPS.toFixed(2) : fcfPerShare.toFixed(2)"
                                disabled
                                class="h-10 flex-1 px-3 text-base text-gray-500 dark:text-gray-300 placeholder:text-gray-400 bg-transparent focus:outline-none cursor-not-allowed"
                            />
                            <div
                                class="flex items-center h-10 px-3 text-xs font-medium text-gray-700 dark:text-gray-200 rounded-r-md shadow-sm bg-gradient-to-r from-gray-100 to-gray-200 dark:from-gray-600 dark:to-gray-700 transition duration-200 hover:brightness-110 hover:scale-105"
                            >
                                $
                            </div>
                        </div>
                    </div>

                    <!-- Yield / EPS Multiple -->
                    <LabeledInput :label="dcfMode === 'EPS' ? 'EPS Multiple:' : 'FCF Yield:'" v-model.number="yieldOrMultiple" :unit="dcfMode === 'EPS' ? 'x' : '%'" type="number" :step="0.1" :min="0" :max="30" />
                    
                    <!-- Growth Rate / EPS Growth -->
                    <LabeledInput :label="dcfMode === 'EPS' ? 'EPS Growth Rate:' : 'FCF/Share Growth Rate:'" v-model.number="growthRate" unit="%" type="number" :step="0.01" :min="0" :max="30" />

                    <!-- Desired Return -->
                    <LabeledInput label="Desired Return:" v-model.number="desiredReturn" unit="%" type="number" :step="0.1" :min="0" :max="50" />
                </div>
            </div>

            <!-- Right Column: Results -->
            <div class="space-y-6 lg:col-span-1">
                <h3 class="text-lg font-semibold mb-2 border-b border-gray-300 dark:border-gray-600 pb-1">Calculation Results</h3>

                <div class="p-5 bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-md">
                    <div class="grid grid-cols-1 sm:grid-cols-2 gap-6">
                        <div class="flex flex-col space-y-1">
                            <h4 class="text-sm font-semibold mb-4 text-gray-500 dark:text-gray-400  tracking-wide">Return from Today's Price:</h4>
                            <span class="text-2xl">{{ returnFromPrice }}</span>
                        </div>

                        <div class="flex flex-col space-y-1">
                            <h4 class="text-sm font-semibold mb-4 text-gray-500 dark:text-gray-400 tracking-wide">Entry Price for {{desiredReturn}}% Annual Return:</h4>
                            <span class="text-2xl">{{ entryPrice }}</span>
                        </div>
                    </div>
                </div>

                <!-- Chart -->
                <div class="bg-gray-50 dark:bg-gray-700 rounded-lg border border-gray-200 dark:border-gray-600 p-2">
                    <LineChart :labels="chartLabels" :series="chartSeries" yAxisName="Price ($)" xAxisLabel="Year" />
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
    import { ref, computed } from "vue";
    import LineChart from "@/components/charts/LineChart.vue";
    import LabeledInput from "@/components/subcomponents/LabeledInput.vue";

    // --- DCF Mode ---
    const dcfMode = ref("EPS");

    // --- Hard Facts ---
    const hardFacts = ref({
        ticker: "AAPL",
        lastFCF: 20000,
        cash: 62000,
        debt: 105000,
        sharesOutstanding: 15500,
        sbcTTM: 1500,
    });

    // --- DCF Parameters ---
    const dcfParams = ref({
        epsGrowth: 5,
        fcfGrowthStatic: 5,
        discountRate: 10,
        terminalGrowthRate: 2.5,
        fcfYield: 5,
        epsMultiple: 20,
    });

    // --- Desired Return ---
    const desiredReturn = ref(15);

    // --- Last EPS ---
    const lastEPS = 1.58;

    // --- Computed Values ---
    const fcfPerShare = computed(() => hardFacts.value.lastFCF / hardFacts.value.sharesOutstanding);
    const fcfYield = computed(() => hardFacts.value.lastFCF / (hardFacts.value.lastFCF + hardFacts.value.cash - hardFacts.value.debt));
    const sbcImpact = computed(() => hardFacts.value.sbcTTM);
    const peRatio = computed(() => (lastEPS > 0 ? 30 / lastEPS : 0)); // placeholder PE, could be market price / EPS

    // --- Conditional v-models ---
    const growthRate = computed({
        get() {
            return dcfMode.value === "EPS" ? dcfParams.value.epsGrowth : dcfParams.value.fcfGrowthStatic;
        },
        set(value) {
            if (dcfMode.value === "EPS") {
                dcfParams.value.epsGrowth = value;
            } else {
                dcfParams.value.fcfGrowthStatic = value;
            }
        },
    });

    const yieldOrMultiple = computed({
        get() {
            return dcfMode.value === "EPS" ? dcfParams.value.epsMultiple : dcfParams.value.fcfYield;
        },
        set(value) {
            if (dcfMode.value === "EPS") {
                dcfParams.value.epsMultiple = value;
            } else {
                dcfParams.value.fcfYield = value;
            }
        },
    });

    // --- Intrinsic Value ---
    const intrinsicValue = computed(() => {
        if (dcfMode.value === "EPS") {
            return lastEPS * (1 + dcfParams.value.epsGrowth / 100) ** 5 * dcfParams.value.epsMultiple;
        } else {
            const fcf = hardFacts.value.lastFCF * (1 + dcfParams.value.fcfGrowthStatic / 100) ** 5;
            const terminalValue = (fcf * (1 + dcfParams.value.terminalGrowthRate / 100)) / (dcfParams.value.fcfYield / 100 - dcfParams.value.terminalGrowthRate / 100);
            return terminalValue / (1 + dcfParams.value.discountRate / 100) ** 5;
        }
    });

    // --- Dynamic Calculation Results ---
    const returnFromPrice = computed(() => {
        const currentPrice = 150;
        return ((intrinsicValue.value / currentPrice - 1) * 100).toFixed(2) + "%";
    });

    const entryPrice = computed(() => {
        const price = intrinsicValue.value / (1 + desiredReturn.value / 100);
        return "$" + price.toFixed(2);
    });

    // --- Chart ---
    const chartLabels = computed(() => Array.from({ length: 5 }, (_, i) => `Year ${i + 1}`));

    const chartSeries = computed(() => {
        const years = 5;
        let values = [];
        if (dcfMode.value === "EPS") {
            for (let i = 1; i <= years; i++) {
                const projectedEPS = lastEPS * Math.pow(1 + dcfParams.value.epsGrowth / 100, i);
                values.push(projectedEPS * dcfParams.value.epsMultiple);
            }
        } else {
            const projectedFCF = hardFacts.value.lastFCF * (1 + dcfParams.value.fcfGrowthStatic / 100);
            for (let i = 1; i <= years; i++) {
                values.push((projectedFCF / hardFacts.value.lastFCF) * 150);
            }
        }
        return [{ name: "Projected Price", data: values, color: "#4F46E5" }];
    });
</script>
