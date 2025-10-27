// Stock Analysis
export const stockFundamentalDataMock = {
  ticker: "AAPL",
  unit: "USD",
  frequency: "yearly", // or "yearly"
  metrics: {
    Revenue: {
      dates: ["2021-01-01", "2021-04-01", "2021-07-01", "2021-10-01"],
      values: [120, 130, 140, 150]
    },
    BasicEPS: {
      dates: Array.from({ length: 10 }, (_, i) => 2014 + i),
      values: [2.5, 2.8, 3.0, 3.5, 3.8, 4.0, 4.3, 4.5, 4.8, 5.0]
    },
    DilutedEPS: {
      dates: Array.from({ length: 10 }, (_, i) => 2014 + i),
      values: [2.6, 3.0, 3.2, 3.7, 4.0, 4.2, 4.5, 4.7, 5.0, 5.2]
    },
    FreeCashFlow: {
      dates: Array.from({ length: 10 }, (_, i) => 2015 + i),
      values: [50, 60, 55, 70, 75, 80, 85, 90, 95, 100]
    },
    OperatingCashFlow: {
      dates: Array.from({ length: 10 }, (_, i) => 2015 + i),
      values: [45, 55, 50, 65, 70, 75, 80, 85, 90, 95]
    },
    Dividend: {
      dates: ["2018", "2019", "2020", "2021", "2022", "2023"],
      values: [1.2, 1.3, 1.4, 1.5, 1.6, 1.7]
    },
    SharePrice: {
      dates: Array.from({ length: 10 }, (_, i) => 2015 + i),
      values: [150, 160, 170, 180, 190, 200, 210, 220, 230, 240]
    },
    SharesOutstanding: {
      dates: [2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024],
      values: [15000000, 14800000, 14600000, 14300000, 14000000, 13700000, 13300000, 12900000, 11500000, 10000000]
    },
    StockRepurchase: {
      dates: [2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024],
      values: [30000000, 32000000, 32500000, 34000000, 35000000, 36000000, 37500000, 39000000, 41000000, 43000000, 47000000, 50000000]
    },
    CostOfRevenue: {
      dates: Array.from({ length: 14 }, (_, i) => 2012 + i),
      values: [40, 42, 44, 45, 47, 49, 50, 52, 54, 55, 57, 59, 60, 62]
    },
    ResearchAndDevelopment: {
      dates: Array.from({ length: 14 }, (_, i) => 2012 + i),
      values: [10, 11, 12, 12, 13, 14, 14, 15, 16, 16, 17, 18, 18, 19]
    },
    Marketing: {
      dates: Array.from({ length: 14 }, (_, i) => 2012 + i),
      values: [8, 9, 9, 10, 11, 11, 12, 12, 13, 13, 14, 14, 15, 15]
    },
    GAndA: {
      dates: Array.from({ length: 14 }, (_, i) => 2012 + i),
      values: [15, 16, 16, 17, 18, 18, 19, 20, 21, 21, 22, 23, 23, 24]
    },
    GrossMargin: {
      dates: Array.from({ length: 16 }, (_, i) => 2010 + i),
      values: [45, 46, 47, 46, 48, 49, 50, 51, 50, 52, 53, 54, 55, 56, 56, 57]
    },
    OperatingMargin: {
      dates: Array.from({ length: 16 }, (_, i) => 2010 + i),
      values: [25, 26, 27, 26, 28, 29, 29, 30, 30, 31, 32, 33, 33, 34, 35, 36]
    },
    ProfitMargin: {
      dates: Array.from({ length: 16 }, (_, i) => 2010 + i),
      values: [15, 16, 17, 16, 18, 19, 19, 20, 20, 21, 21, 22, 23, 23, 24, 25]
    },
    ROCE: {
      dates: Array.from({ length: 14 }, (_, i) => 2012 + i),
      values: [37, 38, 39, 40, 41, 42, 43, 44, 46, 47, 48, 50, 51, 52]
    },
    ROE: {
      dates: Array.from({ length: 14 }, (_, i) => 2012 + i),
      values: [18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 32]
    },
    ROA: {
      dates: Array.from({ length: 14 }, (_, i) => 2012 + i),
      values: [12, 13, 13, 14, 15, 15, 16, 17, 18, 18, 19, 20, 21, 22]
    },
    LongTermDebt: {
      dates: Array.from({ length: 16 }, (_, i) => 2010 + i),
      values: [120, 125, 128, 130, 135, 138, 140, 145, 148, 150, 155, 158, 160, 165, 168, 170]
    },
    ShortTermDebt: {
      dates: Array.from({ length: 16 }, (_, i) => 2010 + i),
      values: [50, 52, 53, 55, 57, 58, 60, 62, 64, 65, 67, 68, 70, 72, 73, 75]
    },
    DebtToEquity: {
      dates: Array.from({ length: 16 }, (_, i) => 2010 + i),
      values: [55, 54, 53, 52, 51, 50, 49, 48, 47, 46, 45, 44, 43, 42, 41, 40]
    },
    InterestCoverage: {
      dates: Array.from({ length: 16 }, (_, i) => 2010 + i),
      values: [8, 8.2, 8.4, 8.6, 8.8, 9, 9.2, 9.4, 9.6, 9.8, 10, 10.2, 10.4, 10.6, 10.8, 11]
    },
    NetDebtToEBITDA: {
      dates: Array.from({ length: 16 }, (_, i) => 2010 + i),
      values: [4.5, 4.3, 4.2, 4.0, 3.9, 3.8, 3.6, 3.5, 3.3, 3.2, 3.0, 2.9, 2.8, 2.6, 2.5, 2.3]
    },
    TotalAssets: {
      dates: Array.from({ length: 16 }, (_, i) => 2010 + i),
      values: [300, 310, 320, 330, 340, 350, 360, 370, 380, 390, 400, 410, 420, 430, 440, 450]
    },
    TotalLiabilities: {
      dates: Array.from({ length: 16 }, (_, i) => 2010 + i),
      values: [170, 175, 178, 180, 185, 188, 190, 195, 198, 200, 205, 208, 210, 215, 218, 220]
    },
    FCFYield: {
      dates: Array.from({ length: 14 }, (_, i) => 2012 + i),
      values: [5, 5.2, 5.5, 5.8, 6, 6.2, 6.5, 6.8, 7, 7.2, 7.5, 7.8, 8, 8.2]
    },
    SBCAdjustedFCFYield: {
      dates: Array.from({ length: 14 }, (_, i) => 2012 + i),
      values: [4, 4.2, 1.5, 3.8, 3, 4.2, 4.5, 4.8, 5, 5.2, 5.5, 6.8, 7, 7.2]
    },
    PERatio: {
      dates: Array.from({ length: 14 }, (_, i) => 2012 + i),
      values: [18, 17, 19, 20, 18, 19, 21, 22, 20, 19, 21, 22, 23, 24]
    },
    EVToEBITDA: {
      dates: Array.from({ length: 14 }, (_, i) => 2012 + i),
      values: [12, 12.5, 12.8, 13, 13.2, 13.5, 13.8, 14, 14.2, 14.5, 14.8, 15, 15.2, 15.5]
    },
    PriceToBook: {
      dates: Array.from({ length: 14 }, (_, i) => 2012 + i),
      values: [3, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 4, 4.1, 4.2, 4.3]
    }
  }
};

export const stockDetailsDataMock = {
  currentPrice: 450.25,
  relChange: 2.15, // % change today
  absChange: 1.25, // $ change today
  lastUpdated: "2025-09-29T14:30:00Z",
  isLive: true,
  performance: {
    "1M": { relStockPriceChange: 5.3, absStockPriceChange: 21.45 },
    "YTD": { relStockPriceChange: 24.7, absStockPriceChange: 88.32 },
    "1Y": { relStockPriceChange: 32.1, absStockPriceChange: 120.50 },
    "3Y": { relStockPriceChange: 140.5, absStockPriceChange: 265.40 },
    "5Y": { relStockPriceChange: -12.3, absStockPriceChange: -55.30 }
  },
  industry: "Semiconductors",
  sector: "Technology",
  country: "USA"
}

export const stockKpiGroupsDataMock = [
  {
    title: 'Valuation',
    kpis: [
      { name: 'Market Capitalization', value: '3T' },
      { name: 'P/E Ratio (TTM/FWD)', value: '26.18 | 27.38' },
      { name: 'P/B & P/S Ratio', value: '6.18 | 7.38' },
      { name: 'EV/EBITDA', value: '20.79' }
    ]
  },
  {
    title: 'Cash Flow',
    kpis: [
      { name: 'FCF Per Share (Yield | Yield w/o SBC)', value: '$12.51 (2.45% | 1.68%)' },
      { name: 'OCF Per Share (Yield)', value: '$12.51 (2.45%)' },
      { name: 'Total Cash & Debt (Ratio)', value: '$12.1B | $6.1B (2.45)' },
      { name: 'Debt-to-FCF', value: '0.78' }
    ]
  },
  {
    title: 'Margins',
    kpis: [
      { name: 'Gross Margin', value: '60%' },
      { name: 'Operating Margin', value: '35%' },
      { name: 'Net Margin', value: '25%' },
      { name: 'FCF & OCF Margin', value: '40% | 29%' }
    ]
  },
  {
    title: 'Growth',
    kpis: [
      { name: 'Revenue Growth (YoY)', value: '15%' },
      { name: 'Net Income Growth (YoY)', value: '20%' },
      { name: 'FCF Growth (YoY)', value: '5%' },
      { name: 'ROCE & ROIC', value: '12% | 11.3%' }
    ]
  },
  {
    title: 'Dividend & Earnings',
    kpis: [
      { name: 'EPS (TTM|FWD)', value: '$9.37 | $8.55' },
      { name: 'Earnings Date', value: '2025-05-03' },
      { name: 'Dividend Yield & Payout Ratio', value: '0.25% | 0.55%' },
      { name: 'Ex-Dividend & Payout date', value: '2025-09-02 | 2025-09-14' }
    ]
  }
]

// Earnings
export const earningsColumnsMock = [
  { key: 'date', name: 'Date' },
  { key: 'epsEstimate', name: 'EPS Est.',  format: 'currency' },
  { key: 'epsReported', name: 'EPS Rep.',  format: 'currency' },
  { key: 'epsDelta', name: 'EPS Δ', format: 'deltaTag' },
  { key: 'revenueEstimate', name: 'Rev. Est.', format: 'currency' },
  { key: 'revenueReported', name: 'Rev. Rep.',  format: 'currency' },
  { key: 'revenueDelta', name: 'Rev. Δ', format: 'deltaTag' },
]

export const earningsCallsMock = [
  {
    date: '2025-08-10',
    epsEstimate: 1.20,
    epsReported: 1.32,
    epsDelta: 10,
    revenueEstimate: '145000000',
    revenueReported: '152000000',
    revenueDelta: 4.8
  },
  {
    date: '2025-05-10',
    epsEstimate: 1.10,
    epsReported: 1.05,
    epsDelta: -4.5,
    revenueEstimate: '999000',
    revenueReported: '9990',
    revenueDelta: -1.4
  },  {
    date: '2025-08-10',
    epsEstimate: 1.20,
    epsReported: 1.32,
    epsDelta: 10,
    revenueEstimate: '99000000',
    revenueReported: '99000000',
    revenueDelta: 4.8
  },
  {
    date: '2025-05-10',
    epsEstimate: 1.10,
    epsReported: 1.05,
    epsDelta: -4.5,
    revenueEstimate: '140000000',
    revenueReported: '138000000',
    revenueDelta: -1.4
  },  
  {
    date: '2025-08-10',
    epsEstimate: 1.20,
    epsReported: 1.32,
    epsDelta: 10,
    revenueEstimate: '145000000',
    revenueReported: '152000000',
    revenueDelta: 4.8
  },
  {
    date: '2025-05-10',
    epsEstimate: 1.10,
    epsReported: 1.05,
    epsDelta: -4.5,
    revenueEstimate: '140000000',
    revenueReported: '138000000',
    revenueDelta: -1.4
  },
  {
    date: '2025-02-10',
    epsEstimate: 1.05,
    epsReported: 1.08,
    epsDelta: 2.9,
    revenueEstimate: '135000000',
    revenueReported: '137000000',
    revenueDelta: 1.5
  },
  {
    date: '2024-11-10',
    epsEstimate: 0.95,
    epsReported: 0.98,
    epsDelta: 3.2,
    revenueEstimate: '130000000',
    revenueReported: '129000000',
    revenueDelta: -0.8
  },{
    date: '2025-08-10',
    epsEstimate: 1.20,
    epsReported: 1.32,
    epsDelta: 10,
    revenueEstimate: '145000000',
    revenueReported: '152000000',
    revenueDelta: 4.8
  },
  {
    date: '2025-05-10',
    epsEstimate: 1.10,
    epsReported: 1.05,
    epsDelta: -4.5,
    revenueEstimate: '140000000',
    revenueReported: '138000000',
    revenueDelta: -1.4
  },
  {
    date: '2025-02-10',
    epsEstimate: 1.05,
    epsReported: 1.08,
    epsDelta: 2.9,
    revenueEstimate: '135000000',
    revenueReported: '137000000',
    revenueDelta: 1.5
  },
  {
    date: '2024-11-10',
    epsEstimate: 0.95,
    epsReported: 0.98,
    epsDelta: 3.2,
    revenueEstimate: '130000000',
    revenueReported: '129000000',
    revenueDelta: -0.8
  },
    {
    date: '2025-02-10',
    epsEstimate: 1.05,
    epsReported: 1.08,
    epsDelta: 2.9,
    revenueEstimate: '135000000',
    revenueReported: '137000000',
    revenueDelta: 1.5
  },
  {
    date: '2024-11-10',
    epsEstimate: 0.95,
    epsReported: 0.98,
    epsDelta: 3.2,
    revenueEstimate: '130000000',
    revenueReported: '129000000',
    revenueDelta: -0.8
  },
    {
    date: '2025-02-10',
    epsEstimate: 1.05,
    epsReported: 1.08,
    epsDelta: 2.9,
    revenueEstimate: '135000000',
    revenueReported: '137000000',
    revenueDelta: 1.5
  },
  {
    date: '2024-11-10',
    epsEstimate: 0.95,
    epsReported: 0.98,
    epsDelta: 3.2,
    revenueEstimate: '130000000',
    revenueReported: '129000000',
    revenueDelta: -0.8
  },
    {
    date: '2025-02-10',
    epsEstimate: 1.05,
    epsReported: 1.08,
    epsDelta: 2.9,
    revenueEstimate: '135000000',
    revenueReported: '137000000',
    revenueDelta: 1.5
  },
  {
    date: '2024-11-10',
    epsEstimate: 0.95,
    epsReported: 0.98,
    epsDelta: 3.2,
    revenueEstimate: '130000000',
    revenueReported: '129000000',
    revenueDelta: -0.8
  },
    {
    date: '2025-02-10',
    epsEstimate: 1.05,
    epsReported: 1.08,
    epsDelta: 2.9,
    revenueEstimate: '135000000',
    revenueReported: '137000000',
    revenueDelta: 1.5
  },
  {
    date: '2024-11-10',
    epsEstimate: 0.95,
    epsReported: 0.98,
    epsDelta: 3.2,
    revenueEstimate: '130000000',
    revenueReported: '129000000',
    revenueDelta: -0.8
  },
    {
    date: '2025-02-10',
    epsEstimate: 1.05,
    epsReported: 1.08,
    epsDelta: 2.9,
    revenueEstimate: '135000000',
    revenueReported: '137000000',
    revenueDelta: 1.5
  },
  {
    date: '2024-11-10',
    epsEstimate: 0.95,
    epsReported: 0.98,
    epsDelta: 3.2,
    revenueEstimate: '130000000',
    revenueReported: '129000000',
    revenueDelta: -0.8
  },
    {
    date: '2025-02-10',
    epsEstimate: 1.05,
    epsReported: 1.08,
    epsDelta: 2.9,
    revenueEstimate: '135000000',
    revenueReported: '137000000',
    revenueDelta: 1.5
  },
  {
    date: '2024-11-10',
    epsEstimate: 0.95,
    epsReported: 0.98,
    epsDelta: 3.2,
    revenueEstimate: '130000000',
    revenueReported: '129000000',
    revenueDelta: -0.8
  }
]

export const earningsScatterSeriesMock = [
  {
    name: 'Revenue',
    data: [
      ["2025 Q1", 120],
      ["2025 Q2", 130],
      ["2025 Q3", 125],
      ["2025 Q4", 140],
      ["2026 Q1", 145],
      ["2026 Q2", 138],
      ["2026 Q3", 150],
      ["2026 Q4", 155]
    ],
    color: '#4F46E5'
  },
  {
    name: 'Revenue Actual',
    data: [
      ["2025 Q1", 115],
      ["2025 Q2", 135],
      ["2025 Q3", 130],
      ["2025 Q4", 138],
      ["2026 Q1", 150],
      ["2026 Q2", 140],
      ["2026 Q3", 155],
      ["2026 Q4", 158]
    ],
    color: '#10B981'
  },
  {
    name: 'EPS Estimate',
    data: [
      ["2025 Q1", 1.2],
      ["2025 Q2", 1.3],
      ["2025 Q3", 1.25],
      ["2025 Q4", 1.4],
      ["2026 Q1", 1.45],
      ["2026 Q2", 1.38],
      ["2026 Q3", 1.50],
      ["2026 Q4", 1.55]
    ],
    color: '#F59E0B'
  },
  {
    name: 'EPS Actual',
    data: [
      ["2025 Q1", 1.15],
      ["2025 Q2", 1.35],
      ["2025 Q3", 1.3],
      ["2025 Q4", 1.38],
      ["2026 Q1", 1.50],
      ["2026 Q2", 1.40],
      ["2026 Q3", 1.53],
      ["2026 Q4", 1.58]
    ],
    color: '#EF4444'
  }
]

export const nextEarningsMock = {
  date: '2025-11-15',
  revenueEstimate: '145000000',
  epsEstimate: '1.4',
  dividendExDate: '2025-12-01',
  expectedDividend: '0.3'
}

// Watchlist
import { formatCurrency } from '@/api/utils/mathUtils.js'

export const watchlistsMock = [
  { 
    name: 'Tech Giants', 
    stocks: [
      { ticker: 'AAPL', company: 'Apple Inc.', marketCap: '$2.5T' },
      { ticker: 'MSFT', company: 'Microsoft Corp.', marketCap: '$2.1T' }
    ],
    upcomingEarnings: [
      { name: 'Apple Inc.', ticker: 'AAPL', epsEstimate: formatCurrency(1.28), epsReported: formatCurrency(1.30), date: '2025-10-10' },
      { name: 'Microsoft Corp.', ticker: 'MSFT', epsEstimate: formatCurrency(2.10), epsReported: formatCurrency(2.15), date: '2025-10-12' }
    ],
    fundamentals: [
      {
        "Ticker": "AAPL",
        "Company": "Apple Inc.",
        "FCF Yield (%)": 5.2,
        "FCF Yield w/o SBC (%)": 4.9,
        "Trailing P/E": 27.5,
        "Forward P/E": 25.0,
        "Price-to-Sales": 7.3,
        "EV/EBITDA": 20.1,
        "Debt/Equity": 1.5,
        "Cash/Debt": 0.8,
        "Revenue Growth (%)": 10.5,
        "EPS Growth (%)": 12.0,
        "FCF Growth (%)": 11.2,
        "ROCE (%)": 18.0,
        "ROIC (%)": 15.5
      },
      {
        "Ticker": "MSFT",
        "Company": "Microsoft Corp.",
        "FCF Yield (%)": 4.8,
        "FCF Yield w/o SBC (%)": 4.5,
        "Trailing P/E": 30.2,
        "Forward P/E": 28.0,
        "Price-to-Sales": 10.1,
        "EV/EBITDA": 22.5,
        "Debt/Equity": 0.8,
        "Cash/Debt": 1.2,
        "Revenue Growth (%)": 11.0,
        "EPS Growth (%)": 13.5,
        "FCF Growth (%)": 12.3,
        "ROCE (%)": 20.0,
        "ROIC (%)": 17.8
      }
    ],
     dipData: {
      '200D': [
        { ticker: 'AAPL', change: 12.5 },
        { ticker: 'MSFT', change: -5.2 },
      ],
      'YTD': [
        { ticker: 'AAPL', change: 18.2 },
        { ticker: 'MSFT', change: 9.4 },
      ],
      '1Y': [
        { ticker: 'AAPL', change: 35.1 },
        { ticker: 'MSFT', change: 28.6 },
      ],
      '5Y': [
        { ticker: 'AAPL', change: 210 },
        { ticker: 'MSFT', change: 180 },
      ]
    }
  },
  { 
    name: 'E-Commerce', 
    stocks: [
      { ticker: 'AMZN', company: 'Amazon.com Inc.', marketCap: '$1.3T' },
      { ticker: 'BABA', company: 'Alibaba Group', marketCap: '$400B' }
    ],
    upcomingEarnings: [
      { name: 'Amazon.com Inc.', ticker: 'AMZN', epsEstimate: formatCurrency(0.85), epsReported: formatCurrency(0.90), date: '2025-10-15' },
      { name: 'Alibaba Group', ticker: 'BABA', epsEstimate: formatCurrency(1.10), epsReported: formatCurrency(1.12), date: '2025-10-18' }
    ],
    fundamentals: [
      {
        "Ticker": "AMZN",
        "Company": "Amazon.com Inc.",
        "FCF Yield (%)": 3.5,
        "FCF Yield w/o SBC (%)": 3.2,
        "Trailing P/E": 60.5,
        "Forward P/E": 55.0,
        "Price-to-Sales": 3.5,
        "EV/EBITDA": 18.0,
        "Debt/Equity": 1.1,
        "Cash/Debt": 0.7,
        "Revenue Growth (%)": 12.0,
        "EPS Growth (%)": 10.0,
        "FCF Growth (%)": 9.8,
        "ROCE (%)": 15.0,
        "ROIC (%)": 13.5
      },
      {
        "Ticker": "BABA",
        "Company": "Alibaba Group",
        "FCF Yield (%)": 4.0,
        "FCF Yield w/o SBC (%)": 3.8,
        "Trailing P/E": 25.0,
        "Forward P/E": 22.5,
        "Price-to-Sales": 5.2,
        "EV/EBITDA": 15.0,
        "Debt/Equity": 0.6,
        "Cash/Debt": 1.0,
        "Revenue Growth (%)": 13.0,
        "EPS Growth (%)": 12.5,
        "FCF Growth (%)": 11.0,
        "ROCE (%)": 16.0,
        "ROIC (%)": 14.8
      }
    ],
     dipData: {
      '200D': [
        { ticker: 'AMZN', change: 8.1 },
        { ticker: 'BABA', change: -3.7 },
      ],
      'YTD': [
        { ticker: 'AMZN', change: -2.3 },
        { ticker: 'BABA', change: 5.6 },
      ],
      '1Y': [
        { ticker: 'AMZN', change: 5.0 },
        { ticker: 'BABA', change: 12.3 },
      ],
      '5Y': [
        { ticker: 'AMZN', change: 90 },
        { ticker: 'BABA', change: 150 },
      ]
    }
  }
]

export const watchlistFundamentalsColumnsMock = [
  { name: "Ticker", key: "Ticker" },
  { name: "Company", key: "Company" },
  { name: "FCF Yield (%)", key: "FCF Yield (%)" },
  { name: "FCF Yield w/o SBC (%)", key: "FCF Yield w/o SBC (%)" },
  { name: "Trailing P/E", key: "Trailing P/E" },
  { name: "Forward P/E", key: "Forward P/E" },
  { name: "Price-to-Sales", key: "Price-to-Sales" },
  { name: "EV/EBITDA", key: "EV/EBITDA" },
  { name: "Debt/Equity", key: "Debt/Equity" },
  { name: "Cash/Debt", key: "Cash/Debt" },
  { name: "Revenue Growth (%)", key: "Revenue Growth (%)" },
  { name: "EPS Growth (%)", key: "EPS Growth (%)" },
  { name: "FCF Growth (%)", key: "FCF Growth (%)" },
  { name: "ROCE (%)", key: "ROCE (%)" },
  { name: "ROIC (%)", key: "ROIC (%)" }
]

export const watchlistEarningsColumnsMock = [
  { name: "Stock Name", key: "name" },
  { name: "Ticker", key: "ticker" },
  { name: "EPS Estimate", key: "epsEstimate" },
  { name: "EPS Reported", key: "epsReported" },
  { name: "Earnings Date", key: "date" }
]

export const watchlistColumnsMock = [
  { name: "Ticker", key: "ticker" },
  { name: "Company", key: "company" },
  { name: "Market Cap", key: "marketCap" }
]