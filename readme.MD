# Project Overview

## 📋 Overview

<!-- toc -->

- [0 DEV Links](#0-dev-links)
- [1 Setup & Installation](#1-setup--installation)
- [2 Tailwind docu](#2-tailwind-docu)
- [3 Way of working](#3-way-of-working)
- [4 Folder structure](#4-folder-structure)
  * [4.1 Notes on this Structure:](#41-notes-on-this-structure)
  * [4.2 Diagram:](#42-diagram)
- [5 TODOs:](#5-todos)

<!-- tocstop -->

## 0 DEV Links

- **Tailwind CSS:** https://tailwindcss.com/plus/ui-blocks?ref=sidebar
    - Grid Layout: https://tailwindcss.com/docs/grid-column
- **ECharts:** https://echarts.apache.org/examples/en/index.html & https://vue-echarts.dev/
    - Inspo competitor: https://flowbite.com/docs/plugins/charts/
- **Headless UI** (Interactive elements and design later with tailwind)
    - *Description*: 
        - Headless UI gives you the logic + accessibility, and you make it look like your dashboard using Tailwind.-
        - Use it whenever you need UI components that are interactive + accessible + unstyled (so you can style with Tailwind). Common examples in dashboards:

            - Tabs → Switch between multiple chart views (e.g., Revenue, EPS, Margins).
            - Dropdowns / Select menus → Pick companies, sectors, or time ranges.
            - Modals / Dialogs → Show a deep dive into a company’s fundamentals when clicking a chart.
            - Disclosure / Accordions → Expandable sections for notes, metrics definitions, or extra data.
            - Menus → Profile/settings menu, export options (CSV, PDF).
            - Combobox / Search → Typeahead for stock ticker search.
- **Heroicons**: https://heroicons.com/
- **Frontend Decisions**:
    - State Management: Pinia Store
    - Backend & Caching: Axios with VueQuery
    - Routing: Vue router
- **Backend Decisions**:
    - API: FastAPI
    - Caching: Redis


## 1 Setup & Installation

- Create vue project: `npm create vite@latest vue-frontend`
- Install tailwind CSS: `npm install tailwindcss @tailwindcss/vite`
- Install VueQuery: `npm install @tanstack/vue-query`
- Install VueRouter: `npm install vue-router@4`
- Install pinia: `npm install pinia`
- Install echarts: `npm install echarts`
- Install headless ui: npm install @headlessui/vue
- Install HeroIcons: npm install @heroicons/vue




## 2 Tailwind docu
- Utility examples: https://tailwindcss.com/plus/ui-blocks?ref=sidebar

## 3 Way of working
- Data: 
    - Mock data using pinia store
- UI:
    - Build new UI components
    - Build layouts and page using components
- Backend:
    - API calls using FastAPI backend
    - Wrap API calls using VueQuery in *api/composables*
    - Integrate into Pinia Store, replacing mocked data

## 4 Folder structure
### 4.1 Notes on this Structure: 
**components/charts/**:
- Each chart type is a reusable component with props like :data and :options.
- Keeps ECharts setup isolated and easy to swap.

**components/ui/**:
- Contains Headless UI components styled with Tailwind.
- Example: Dropdown.vue can handle company selection, Tabs.vue switches between Revenue, EPS, etc.

**composables/**:
- Functions like useStockData() wrap Vue Query calls.
- useCharts() can handle common chart helpers (colors, tooltips, formatting).

**views/** and **layouts/**:
- views/ = the main views (Dashboard, Company details, Compare stocks).
- layouts/ = reusable layouts with navigation, sidebars, cards. Pages slot into layouts.

**stores/**
- Pinia stores manage shared state (selected company, selected metrics, filters).
- Keeps components decoupled.

**api/**
- Centralizes Axios instance (base URL, headers, auth).
- All API calls in one place makes maintenance easy.

### 4.2 Diagram:
```text
src/
├─ api/                          # All backend/data-related code (Axios + Vue Query API calls)
│  ├─ index.js                   # Axios instance / base config
│  ├─ stock.js                   # Raw stock-related API calls
│  ├─ utils/                    # Pure JS helpers for transforming API data
│  │   └─ formatStockData.js
│  └─ composables/               # Vue composables/hooks using API functions
│      ├─ useStockData.js
│      └─ useStockMetrics.js
|
├─ assets/               # Images, logos, static assets
|
├─ components/           # Reusable Vue components
|   ├─ charts/           # Chart components
|   |   ├─ BarChart.vue
|   |   ├─ LineChart.vue
|   |   └─ PieChart.vue
|   |
|   ├─ ui/               # UI primitives using Headless UI
|   |   ├─ Dropdown.vue
|   |   ├─ Tabs.vue
|   |   └─ Modal.vue
|   |
|   ├─ tables/           # Reusable table components
|   |   └─ FinancialTable.vue
|   |
|   └─ common/           # Buttons, cards, badges, etc.
|       ├─ Card.vue
|       └─ Button.vue
|
├─ composables/          # Reusable logic hooks
|   ├─ useStockData.js   # Fetch stock fundamentals via Vue Query
|   └─ useCharts.js      # Common chart helpers
|
├─ layouts/              # Page layouts
|   ├─ DashboardLayout.vue
|   └─ MainLayout.vue
|
├─ views/                # Page views (used by Vue Router)
|   ├─ Dashboard.vue
|   ├─ Company.vue
|   └─ Compare.vue
|
├─ router/               # Vue Router setup
|   └─ index.js
|
├─ stores/               # Pinia stores
|   └─ stockStore.js
|
├─ styles/               # Tailwind config + global styles
|   └─ globals.css
|
├─ App.vue
├─ main.js
```

## 5 TODOs:
- Integrate hard-coded data to pinia store & revise code for duplicates and/or bad design
    - e.g. percentage calculation and currency selection moved to central js scripts --> identify re-use potential will be else a big pain later on!
    - Progress:
        - TODO: Deltas entfernen in earningstab pop-up und da den control fixen, dann maybe etwas leaner den modal machen bzw. arg handling im modal unsauber
        - StockAnalysis (StockAutocomplete, StockDetails, StockKPIs, ContentTabs, ChartFullscreenModal, ChartCard, ChartSections) 
        - Dont like & TODO: Charts (ka ob no touch oder?), 