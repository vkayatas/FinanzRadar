# FinanzRadar

A full-stack web application for **fundamental analysis of US public companies**. It fetches and parses SEC EDGAR filings (10-K, 10-Q) to extract financial metrics, stores them in a local feature store, and visualizes the data through an interactive Vue.js dashboard.

## What It Does

FinanzRadar pulls structured financial data directly from [SEC EDGAR XBRL APIs](https://data.sec.gov/) — no third-party data vendors required for core fundamentals. The backend maps raw US-GAAP concepts (e.g. `RevenueFromContractWithCustomerExcludingAssessedTax`) to normalized metric names (e.g. `Revenue`) with company-specific overrides where needed.

**Key financial metrics extracted:**

| Category | Metrics |
|---|---|
| **Income Statement** | Revenue, Gross Profit, Operating Income, Net Income, EPS (Basic & Diluted), R&D, SG&A, Cost of Revenue |
| **Balance Sheet** | Total Assets, Total Liabilities, Stockholders' Equity, Cash, Current Assets/Liabilities, Short/Long-Term Debt |
| **Cash Flow** | Operating Cash Flow, Capital Expenditures, Stock-Based Compensation, Dividends Paid, Stock Buybacks |
| **Derived** | Custom computed metrics built on top of the raw data (margins, ratios, etc.) |

The Vue frontend then renders these metrics as interactive charts — line charts for historical trends, bar charts for comparisons, scatter plots for EPS estimates vs. actuals, and more.

## Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│  Vue 3 Frontend (port 5173)                                      │
│  Tailwind CSS · ECharts · Pinia · Vue Query · Vue Router         │
│                                                                  │
│  Views: Stock Analysis · Watchlist · Portfolio · Home             │
│  Charts: Line, Bar, Stacked Area, Scatter, Nightingale, Donut   │
└──────────────────────┬───────────────────────────────────────────┘
                       │ Axios (REST)
┌──────────────────────▼───────────────────────────────────────────┐
│  FastAPI Backend (port 8000)                                     │
│  Endpoints: /fundamentals_history · /stock_info · /kpis ·       │
│             /earnings                                            │
└──────────────────────┬───────────────────────────────────────────┘
                       │ Parquet read
┌──────────────────────▼───────────────────────────────────────────┐
│  Local Feature Store (Parquet)                                   │
│  Partitioned by ticker & form: fundamentals/ · info/ · kpis/ ·  │
│  earnings/                                                       │
└──────────────────────┬───────────────────────────────────────────┘
                       │ Populated by data pipeline
┌──────────────────────▼───────────────────────────────────────────┐
│  Data Sources                                                    │
│  • SEC EDGAR XBRL API (company facts, submissions)               │
│  • Yahoo Finance (market cap, stock info, earnings estimates)    │
└──────────────────────────────────────────────────────────────────┘
```

## Tech Stack

### Backend (Python)
- **FastAPI** — REST API serving preprocessed financial data
- **Pandas** — data wrangling and metric computation
- **Parquet** — columnar storage for the local feature store
- **SEC EDGAR API** — direct XBRL fact retrieval per CIK
- **yfinance** — supplementary market data (market cap, earnings estimates)

### Frontend (JavaScript)
- **Vue 3** (Composition API) with **Vite**
- **Tailwind CSS** — utility-first styling
- **ECharts** — rich interactive charting
- **Pinia** — state management
- **Vue Query** (@tanstack/vue-query) — async data fetching and caching
- **Vue Router** — SPA routing
- **PrimeVue** — data tables and UI components
- **Headless UI + Heroicons** — accessible interactive elements
- **Fuse.js** — fuzzy ticker search
- **vue-i18n** — internationalization (EN/DE)

## Project Structure

```
FinanzRadar/
├── backend/
│   ├── main.py                      # FastAPI app with endpoints
│   ├── main_update_database.py      # Data pipeline: fetch → transform → store
│   ├── main_fetch_tickers.py        # Ticker list management
│   ├── parsers/
│   │   ├── sec.py                   # SEC EDGAR XBRL data fetching
│   │   ├── sec_processing.py        # US-GAAP concept → metric mapping & merging
│   │   ├── yahoo_processing.py      # yfinance data integration
│   │   └── tickers_fetching.py      # Ticker resolution
│   └── utils/
│       ├── data_viz_preprocessing.py # Transform DataFrames into frontend-ready JSON
│       ├── math_utils.py            # Financial calculations
│       ├── date_utils.py            # Date helpers
│       ├── pandas_utils.py          # DataFrame utilities
│       └── config/
│           ├── config.py            # Metric concept mappings & constants
│           └── fundamentals_config.json  # Pipeline configuration
│
├── vue-frontend/
│   └── src/
│       ├── api/                     # Axios calls + data transform utilities
│       ├── components/
│       │   ├── charts/              # ECharts wrappers (Line, Bar, Scatter, ...)
│       │   ├── tables/              # PrimeVue data tables
│       │   ├── tabs/                # Tab-based content sections
│       │   ├── subcomponents/       # KPI cards, chart cards, modals
│       │   └── ui/                  # Navbar, dropdowns, search autocomplete
│       ├── stores/                  # Pinia stores (stock, fundamentals, earnings, ...)
│       ├── views/                   # Pages: StockAnalysis, Watchlist, Portfolio, Home
│       ├── locales/                 # i18n translations (en, de)
│       └── router/                  # Vue Router config
│
└── logs/                            # Application logs
```

## Setup & Installation

### Option A: Docker Compose (recommended)

```bash
docker compose up --build
```

This starts both services:
- **Backend** (FastAPI) → `http://localhost:8000`
- **Frontend** (Nginx) → `http://localhost:3000` (proxies `/api/` to backend)

### Option B: Local development

#### Backend (uv)

```bash
cd backend
uv sync            # creates .venv and installs dependencies from pyproject.toml
```

#### Frontend

```bash
cd vue-frontend
npm install
```

## Running (local dev)

### 1. Populate the feature store

```bash
cd backend
uv run python main_update_database.py
```

This fetches SEC EDGAR data and Yahoo Finance data for all configured tickers, processes them, and writes Parquet files to the feature store.

### 2. Start the API server

```bash
cd backend
uv run uvicorn main:app --host 0.0.0.0 --port 8000
```

The FastAPI server starts on `http://localhost:8000`.

### 3. Start the frontend

```bash
cd vue-frontend
npm run dev
```

The Vite dev server starts on `http://localhost:5173`.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/fundamentals_history/{ticker}?form=10-K` | Historical fundamental metrics (annual or quarterly) |
| GET | `/stock_info/{ticker}` | Company info and metadata |
| GET | `/kpis/{ticker}` | Key performance indicator groups |
| GET | `/earnings/{ticker}` | Earnings history, EPS estimates vs. actuals, next earnings date |

## How SEC Data Parsing Works

1. **Ticker → CIK**: Resolves the stock ticker to a SEC Central Index Key using the SEC company tickers endpoint
2. **Fetch XBRL facts**: Calls the SEC EDGAR companyfacts API to get all reported US-GAAP facts for that company
3. **Concept mapping**: Each target metric (e.g. `Revenue`) maps to a ranked list of US-GAAP concepts with fallback priority — if the primary concept is missing, the next one is tried
4. **Company overrides**: Some companies use non-standard tags; a per-ticker override config handles these cases
5. **Temporal filtering**: Entries are filtered by filing type (10-K/10-Q) and validated by date range to ensure correct annual/quarterly periods
6. **Pivot & enrich**: Metrics are pivoted into a wide-format DataFrame, enriched with market cap from Yahoo Finance, and custom derived metrics are computed
