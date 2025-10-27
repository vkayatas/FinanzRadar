//Config
export const sectionConfigs = {
  growthAndInvestment: {
    title: "Growth & Investment Metrics",
    charts: [
      { metric: "Revenue", color: "#4F46E5", title: "Revenue Growth", chartType: "bar", yAxisName: "Revenue ($M)" },
      {metrics: [
          { metric: "BasicEPS", color: "#10B981" },
          { metric: "DilutedEPS", color: "#6366F1" }
        ],
        title: "EPS Growth", chartType: "bar", yAxisName: "EPS Growth"},
      { metrics: [
          { metric: "CostOfRevenue", color: "#F43F5E" },
          { metric: "ResearchAndDevelopment", color: "#6366F1" },
          { metric: "Marketing", color: "#F59E0B" },
          { metric: "GAndA", color: "#10B981" }
        ],
        title: "Total Expenses", chartType: "stackedbar", yAxisName: "Expenses ($M)"
      },
      { metric: "SharePrice", color: "#10B981", title: "Share Price", chartType: "line", yAxisName: "Price per Share", areaStyle: true  },
    ]
  },
  cashFlowAndLiquidity: {
    title: "Cash Flow & Liquidity Metrics",
    charts: [
      { metrics: [
          { metric: "FreeCashFlow", color: "#F97316" },
          { metric: "OperatingCashFlow", color: "#6366F1" }
        ],
        title: "Cash Flow Growth", chartType: "line", yAxisName: "FCF ($M)"},
      { metric: "SharesOutstanding", color: "#10B981", title: "Shares Outstanding", chartType: "bar", yAxisName: "Shares" },
      { metric: "StockRepurchase", color: "#EF4444", title: "Repurchase of Common Stock", chartType: "bar", yAxisName: "Repurchase ($M)" },
      { metric: "Dividend", color: "#6366F1", title: "Dividend and Dividend Yield", chartType: "area", yAxisName: "Dividend ($)" }
    ]
  },
  profitability: {
    title: "Profitability Metrics",
    charts: [
      { metrics: [
          { metric: "GrossMargin", color: "#10B981" },
          { metric: "OperatingMargin", color: "#F59E0B" },
          { metric: "ProfitMargin", color: "#EF4444" }
        ],
        title: "Margins", chartType: "line", yAxisName: "Margins (%)"
      },
      { metrics: [
          { metric: "ROCE", color: "#6366F1" },
          { metric: "ROE", color: "#10B981" },
          { metric: "ROA", color: "#F59E0B" }
        ],
        title: "Return on Capital Employed, Equity & Assets", chartType: "line", yAxisName: "Ratio (%)"
      }
    ]
  },
  debtAndRisk: {
    title: "Debt & Risk",
    charts: [
      { metrics: [
          { metric: "LongTermDebt", color: "#6366F1" },
          { metric: "ShortTermDebt", color: "#EF4444" }
        ],
        title: "Debt Overview", chartType: "stackedbar", yAxisName: "Debt ($M)"
      },
      { metrics: [
          { metric: "DebtToEquity", color: "#10B981" },
          { metric: "InterestCoverage", color: "#F59E0B" },
          { metric: "NetDebtToEBITDA", color: "#EF4444" }
        ],
        title: "Debt Indicators", chartType: "line", yAxisName: "Ratio"
      },
      { metrics: [
          { metric: "TotalAssets", color: "#10B981" },
          { metric: "TotalLiabilities", color: "#EF4444" }
        ],
        title: "Assets VS. Liabilities", chartType: "bar", yAxisName: "Amount ($M)"
      }
    ]
  },
  valuation: {
    title: "Valuation Metrics",
    charts: [
      { metrics: [
          { metric: "FCFYield", color: "#6366F1" },
          { metric: "SBCAdjustedFCFYield", color: "#EF4444" }
        ],
        title: "Free Cash Flow Yield [%]", chartType: "line", yAxisName: "FCF Yield (%)"
      },
      { metric: "PERatio", color: "#10B981", title: "P/E Ratio", chartType: "line", yAxisName: "P/E Ratio" },
      { metrics: [
          { metric: "EVToEBITDA", color: "#F59E0B" },
          { metric: "PriceToBook", color: "#6366F1" }
        ],
        title: "Fundamental Valuation Indicators", chartType: "line", yAxisName: "Ratio"
      }
    ]
  }
};

// helper to format echart data correctly
export function buildChartData(stockData, metricName, color = '#4F46E5', chartType = 'line') {
  const metric = stockData.metrics[metricName];
  if (!metric) return [];

  // CASE 1: scatter (already formatted)
  if (chartType === 'scatter' && Array.isArray(metric)) {
    // Each item is already a { name, data: [[x, y]], color }
    return metric.map(m => ({
      name: m.name,
      data: m.data,
      color: m.color || color,
    }));
  }

  // CASE 2: standard time-series
  if (metric.values && metric.dates) {
    return [
      {
        name: metricName,
        data: metric.values,
        labels: metric.dates,
        color
      }
    ];
  }

  console.warn(`[buildChartData] Unexpected metric format for ${metricName}`);
  return [];
}


// Generic Tailwind/ECharts-friendly palette
const defaultColors = [
  '#4F46E5', '#F59E0B', '#10B981', '#EF4444',
  '#3B82F6', '#8B5CF6', '#F97316', '#22D3EE'
];

// Delta Tag time ranges
const deltaTimeRanges = ['1Y', '3Y', '5Y', 'All'];

/**
 * Normalizes chart data into the standard ECharts-compatible format:
 *   [{ name: string, data: number[], color: string }]
 */
export function toEchartsDataFormat(data, title = 'Default Series', colors = defaultColors) {
  if (!data) return [];

  // Already in { name, data } format
  if (Array.isArray(data) && data.length > 0 && data[0]?.data) return data;

  // Array of arrays
  if (Array.isArray(data)) {
    if (Array.isArray(data[0])) {
      return data.map((d, i) => ({
        name: `Series ${i + 1}`,
        data: d,
        color: colors[i % colors.length],
      }));
    }

    // Flat array
    return [{ name: title, data, color: colors[0] }];
  }

  return [];
}

/**
 * Computes year-over-year (or N-year) percent deltas
 * @param {number[]} data - numeric array (e.g., revenue per year)
 * @param {Array<string|number>} labels - array of years or timestamps
 * @returns {Object} { '1Y': {percent}, '3Y': {percent}, '5Y': {percent}, 'All': {percent} }
 */
export function computeDeltas(data, labels) {
  if (!data || data.length === 0) return {};

  const years = labels.map(l =>
    typeof l === 'number' ? l : new Date(l).getFullYear()
  );
  const result = {};

  const delta = numYears => {
    if (years.length < numYears + 1) return null;
    const startIndex = years.length - numYears - 1;
    const endIndex = years.length - 1;
    if (startIndex < 0) return null;
    const startValue = data[startIndex];
    const endValue = data[endIndex];
    if (startValue == null || endValue == null) return null;
    return ((endValue - startValue) / startValue) * 100;
  };

  deltaTimeRanges.forEach(label => {
    const numYears = label === 'All' ? years.length - 1 : parseInt(label);
    result[label] = { percent: delta(numYears) };
  });

  return result;
}

