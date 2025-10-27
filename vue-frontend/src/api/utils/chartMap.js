import BarChart from "@/components/charts/BarChart.vue";
import LineChart from "@/components/charts/LineChart.vue";
import StackedBarChart from "@/components/charts/StackedBarChart.vue";
import StackedAreaChart from "@/components/charts/StackedAreaChart.vue";
import ScatterChart from "@/components/charts/ScatterChart.vue";

export const chartMap = {
  bar: BarChart,
  line: LineChart,
  stackedbar: StackedBarChart,
  area: StackedAreaChart,
  scatter: ScatterChart
};
