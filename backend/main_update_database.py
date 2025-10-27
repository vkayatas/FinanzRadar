import time
import requests
import pandas as pd 
from datetime import datetime
from functools import lru_cache
from typing import Optional, Dict, List

CACHE_SIZE = 128

# TODO: Fallback concept
# -------------------------------------------------------------
# Step 5: GAAP concept mappings 
# -------------------------------------------------------------
METRICS_CONCEPTS = {
    # Balance Sheet
    "TotalCurrentAssets": ["AssetsCurrent"],
    "CashAndCashEquivalents" : ["CashAndCashEquivalentsAtCarryingValue"],
    "TotalAssets": ["Assets"],
    "ShortTermDebt": ["LongTermDebtCurrent", "DebtCurrent"],
    "TotalCurrentLiabilities": ["LiabilitiesCurrent"],
    "LongTermDebt": ["LongTermDebtNoncurrent", "LongTermDebt"],
    "TotalLiabilities": ["Liabilities"], 
    "StockholdersEquity": ["StockholdersEquity"],
    
    # Operations / Income Statement
    "Revenue": ["RevenueFromContractWithCustomerExcludingAssessedTax", "Revenues"],
    "ResearchAndDevelopment": ["ResearchAndDevelopmentExpense"],
    #"SalesAndMarketing": ["SellingAndMarketingExpense"],
    #"GAndA": ["GeneralAndAdministrativeExpense"],
    "CostOfRevenue": ["CostOfGoodsAndServicesSold", "CostOfGoodsSold","CostOfRevenue"],
    "GrossProfit": ["GrossProfit"],
    "TotalOperatingExpenses": ["CostsAndExpenses", "OperatingExpenses"],
    "OperatingIncome": ["OperatingIncomeLoss"],
    "NonOperatingIncomeExpense": ["NonoperatingIncomeExpense"],
    "DepreciationAmortization": ["DepreciationAmortization", "Depreciation", "DepreciationDepletionAndAmortization"],
    "NetIncome": ["ProfitLoss", "NetIncomeLoss"],
    "BasicEps": ["EarningsPerShareBasic", "BasicEarningsLossPerShare"],
    "DilutedEps": ["EarningsPerShareDiluted", "DilutedEarningsLossPerShare"],
    "SharesOutstandingBasic": ["WeightedAverageNumberOfSharesOutstandingBasic"],
    "SharesOutstandingDiluted": ["WeightedAverageNumberOfDilutedSharesOutstanding"],
    "SharesOutstanding": ["CommonStockSharesOutstanding", "NumberOfSharesOutstanding"],
    
    # Cashflow
    "StockBasedCompensation": ["ShareBasedCompensation"],
    "OperatingCashFlow": ["NetCashProvidedByUsedInOperatingActivities"],
    "TotalCash": ["CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents"],
    "DividendsPaid": ["PaymentsOfDividends", "PaymentsOfDividendsCommonStock"],
    "StockBuybacks": ["PaymentsForRepurchaseOfCommonStock"], 
    "CapitalExpenditures": ["PaymentsToAcquirePropertyPlantAndEquipment", "PaymentsToAcquireProductiveAssets"], # "PaymentsToAcquireProductiveAssets", "CapitalExpenditures"
    #"InterestPaid": ["CashPaidForInterest"], #TODO: Unsure and unnecessary
}

COMPANY_TAG_OVERRIDES = {
    # Add more companies/metrics manually or later automatically
}

CUSTOM_METRICS = [
    # -----------------------------------
    # CASH FLOW
    # -----------------------------------
    {
        "columns": ["OperatingCashFlow", "CapitalExpenditures"],
        "func": lambda ocf, capex: ocf.sub(capex, fill_value=0),
        "result_col": "FreeCashFlow",
    },

    # -----------------------------------
    # PROFITABILITY MARGINS
    # -----------------------------------
    {
        "columns": ["Revenue", "CostOfRevenue"],
        "func": lambda rev, cor: (rev.sub(cor, fill_value=0)).div(rev.replace(0, pd.NA)).mul(100),
        "result_col": "GrossMargin",
    },
    {
        "columns": ["OperatingIncome", "Revenue"],
        "func": lambda op_inc, rev: op_inc.div(rev.replace(0, pd.NA)).mul(100),
        "result_col": "OperatingMargin",
    },
    {
        "columns": ["NetIncome", "Revenue"],
        "func": lambda net_inc, rev: net_inc.div(rev.replace(0, pd.NA)).mul(100),
        "result_col": "ProfitMargin",
    },

    # -----------------------------------
    # RETURNS
    # -----------------------------------
    {
        "columns": ["OperatingIncome", "TotalAssets", "TotalCurrentLiabilities"],
        "func": lambda op_inc, assets, curr_liab: op_inc.div((assets - curr_liab).replace(0, pd.NA)).mul(100),
        "result_col": "ROCE",
    },
    {
        "columns": ["NetIncome", "TotalAssets"],
        "func": lambda net_inc, assets: net_inc.div(assets.replace(0, pd.NA)).mul(100),
        "result_col": "ROA",
    },
    {
        "columns": ["NetIncome", "StockholdersEquity"],
        "func": lambda net_inc, equity: net_inc.div(equity.replace(0, pd.NA)).mul(100),
        "result_col": "ROE",
    },
    #{
    #     "columns": ["OperatingIncome", "TotalDebt", "StockholdersEquity", "CashAndCashEquivalents", "TaxRate"],
    #     "func": lambda op_inc, debt, equity, cash, tax: (
    #         (op_inc * (1 - tax.fillna(0))).div((debt + equity - cash).replace(0, pd.NA)).mul(100)
    #     ),
    #     "result_col": "ROIC",
    # },

    # -----------------------------------
    # LEVERAGE / COVERAGE
    # -----------------------------------
    {
        "columns": ["LongTermDebt", "ShortTermDebt", "StockholdersEquity"],
        "func": lambda ltd, std, equity: (ltd.add(std, fill_value=0)).div(equity.replace(0, pd.NA)),
        "result_col": "DebtToEquity",
    },
    # InterestPaid not in METRICS_CONCEPTS → skip if missing
    {
        "columns": ["OperatingIncome", "InterestPaid"],
        "func": lambda op_inc, interest: op_inc.div(interest.replace(0, pd.NA)) if interest is not None else pd.NA,
        "result_col": "InterestCoverage",
    },
    {
        "columns": ["LongTermDebt", "ShortTermDebt", "CashAndCashEquivalents", "OperatingIncome", "DepreciationAmortization"],
        "func": lambda ltd, std, cash, op_inc, dep: (
            (ltd.add(std, fill_value=0) - cash).div((op_inc + dep.fillna(0)).replace(0, pd.NA))
        ),
        "result_col": "NetDebtToEBITDA",
    },


    # -----------------------------------
    # CASH FLOW YIELDS
    # -----------------------------------
    # {
    #     "columns": ["FreeCashFlow", "TotalAssets"],
    #     "func": lambda fcf, assets: fcf.div(assets.replace(0, pd.NA)).mul(100),
    #     "result_col": "FCFYield",
    # },
    # {
    #     "columns": ["StockBasedCompensation", "FreeCashFlow", "TotalAssets"],
    #     "func": lambda sbc, fcf, assets: (fcf.add(sbc, fill_value=0)).div(assets.replace(0, pd.NA)).mul(100),
    #     "result_col": "SBCAdjustedFCFYield",
    # },

    # -----------------------------------
    # VALUATION
    # -----------------------------------
    # {
    #     "columns": ["MarketCap", "NetIncome"],
    #     "func": lambda mc, ni: mc.div(ni.replace(0, pd.NA)),
    #     "result_col": "PERatio",
    # },
    # placeholders for ratios computed from other inputs if available
    # {
    #     "columns": ["MarketCap", "TotalDebt", "CashAndCashEquivalents", "OperatingIncome", "Depreciation", "Amortization"],
    #     "func": lambda mc, debt, cash, op_inc, dep, amort: (
    #         (mc + debt - cash).div((op_inc + dep.fillna(0) + amort.fillna(0)).replace(0, pd.NA))
    #     ),
    #     "result_col": "EVToEBITDA",
    # },
    # {
    #     "columns": ["MarketCap", "TotalAssets", "TotalLiabilities"],
    #     "func": lambda mc, assets, liab: mc.div((assets - liab).replace(0, pd.NA)),
    #     "result_col": "PriceToBook",
    # }
    # {
    #     "columns": ["PERatio", "EPSGrowth"],
    #     "func": lambda pe, growth: pe.div(growth.replace(0, pd.NA)).round(2),
    #     "result_col": "PEGRatio",
    # },
    # {
    #     "columns": ["MarketCap", "TotalDebt", "CashAndCashEquivalents", "Revenue"],
    #     "func": lambda mc, debt, cash, rev: ((mc + debt - cash).div(rev.replace(0, pd.NA))).round(2),
    #     "result_col": "EVToSales",
    # }
]

# -------------------------------------------------------------
# Global headers – SEC requires a descriptive User-Agent
# -------------------------------------------------------------
HEADERS = {
    'User-Agent': 'FinDataFetcher/1.0 (contact@example.com)',
    'Accept': 'application/json'
}

# -------------------------------------------------------------
# Utility: safely make requests with retries
# -------------------------------------------------------------
    
def filter_items_by_years(items: List[Dict], number_of_years: int) -> List[Dict]:
    if not items:
        return []

    # Sort descending by end date (string can be parsed directly)
    sorted_items = sorted(items, key=lambda x: x["end"], reverse=True)

    # Convert latest 'end' to datetime and compute year bounds
    latest_date = pd.to_datetime(sorted_items[0]["end"], errors="coerce")
    if pd.isna(latest_date):
        return sorted_items  # fail-safe: return as-is if parsing fails

    max_year = latest_date.year
    min_year = max_year - number_of_years + 1

    # Keep only those where end-year >= min_year
    filtered = [
        item for item in sorted_items
        if pd.to_datetime(item["end"], errors="coerce").year >= min_year
    ]

    return filtered


def safe_request(url: str, retries: int = 3, backoff: float = 0.5) -> Optional[dict]:
    for attempt in range(retries):
        try:
            r = requests.get(url, headers=HEADERS, timeout=10)
            if r.status_code == 200:
                return r.json()
        except requests.exceptions.RequestException as e:
            print(f"Request failed ({attempt+1}/{retries}): {e}")
        time.sleep(backoff * (2 ** attempt))  # exponential backoff
    return None

# -------------------------------------------------------------
# Step 1: Get CIK from ticker (cached)
# -------------------------------------------------------------
def get_sec_submissions(cik: str) -> dict:
    url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    return safe_request(url) or {}

@lru_cache(maxsize=CACHE_SIZE)
def get_ticker_mapping() -> dict:
    url = "https://www.sec.gov/files/company_tickers.json"
    return safe_request(url) or {}

@lru_cache(maxsize=None)
def get_cik_from_ticker(ticker: str) -> Optional[str]:
    ticker = ticker.lower()
    data = get_ticker_mapping()
    for entry in data.values():
        if entry["ticker"].lower() == ticker:
            return str(entry["cik_str"]).zfill(10)
    return None

# -------------------------------------------------------------
# Step 2: Fetch all US GAAP data for a company (cached)
# -------------------------------------------------------------
@lru_cache(maxsize=CACHE_SIZE)
def get_all_us_gaap_data(cik: str) -> Optional[dict]:
    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
    return safe_request(url)

# -------------------------------------------------------------
# Step 3: Generic metric fetcher with filing type selection
# -------------------------------------------------------------
def sec_metrics_to_dataframe(metrics, ticker: str):
    df = pd.DataFrame({
        metric: {entry["end"]: entry["val"] for entry in values}
        for metric, values in metrics.items()
    }).sort_index(ascending=False)
    df.index.name = "Period End"
    df["symbol"] = ticker
    
    return df

def preprocess_us_gaap(us_gaap: dict, filing_type: str, allowed_units = ["USD", "shares", "USD/shares"]) -> Dict[str, List[dict]]:
    """
    Preprocess US GAAP data for a given filing type.
    Returns a dict: concept -> list of items with 'end' and 'val'.
    """
    preprocessed = {}
    
    for concept, concept_data in us_gaap.items():
        units = concept_data.get("units", {})
        unit_to_use = next((u for u in allowed_units if u in units), None)
        
        if not unit_to_use:
            continue
        
        # Filter only relevant items once
        # filtered_items = [
        #     {"end": i["end"], "val": i["val"]}
        #     for i in units[unit_to_use]
        #     if i.get("form") == filing_type and "val" in i and "end" in i
        # ]

        filtered_items = [i for i in units[unit_to_use] if i.get("form") == filing_type and "val" in i and "end" in i]
        
        if filtered_items:
            preprocessed[concept] = filtered_items
    
    return preprocessed

# -------------------------------------------------------------
# Step 4: Custom metric computations
# -------------------------------------------------------------
def apply_custom_metrics(df: pd.DataFrame, metrics: List[Dict]) -> pd.DataFrame:
    for metric in metrics:
        cols = metric["columns"]
        func = metric["func"]
        result_col = metric["result_col"]
        drop_inputs = metric.get("drop_inputs", False)

        # Identify missing columns
        missing_cols = [c for c in cols if c not in df.columns]

        if missing_cols:
            # Strict mode: skip optional metrics with missing inputs, fill with NA
            print(f"Warning: Missing columns for '{result_col}': {missing_cols}. Filling with NA.")
            df[result_col] = pd.NA
            continue

        # Apply vectorized computation
        try:
            df[result_col] = func(*[df[c] for c in cols]).round(2)
        except Exception as e:
            raise TypeError(
                f"Custom metric '{result_col}' failed during vectorized computation: {e}\n"
                f"Ensure the function operates on pandas Series, not scalars."
            )

        # Optionally drop input columns
        if drop_inputs:
            df.drop(columns=cols, inplace=True, errors="ignore")

    return df


# -------------------------------------------------------------
# Step 5: Main metric fetchers
# -------------------------------------------------------------
def get_company_metrics_history(ticker: str, number_of_years: int = 5, filing_type: str = "10-K", allowed_periods: Optional[list[str]] = None) -> pd.DataFrame:
    # Step 1: Get CIK
    cik = get_cik_from_ticker(ticker)
    if not cik:
        raise ValueError(f"Invalid ticker: {ticker}")

    # Step 2: Fetch SEC GAAP data
    data = get_all_us_gaap_data(cik)
    if not data:
        raise RuntimeError(f"Failed to fetch GAAP data for {ticker}")

    us_gaap = data["facts"]["us-gaap"]
    
    # Step 3: Preprocess once
    preprocessed = preprocess_us_gaap(us_gaap, filing_type)

    # Step 4: Merge metrics
    metrics = {}
    for metric, default_concepts in METRICS_CONCEPTS.items():
        combined_items = []  # list to preserve ranking order

        # Step 4a: Determine the ranked list of concepts
        override_list = COMPANY_TAG_OVERRIDES.get(ticker.upper(), {}).get(metric, [])

        concepts = override_list + [c for c in default_concepts if c not in override_list]

        # Step 4b: Merge items with fallback ranking
        combined_map = {}  # key = end date, value = {"end": date, "val": value}

        for concept in concepts:
            if concept not in preprocessed:
                continue

            for item in preprocessed[concept]:
                end_date = item["end"]
                val = item["val"]

                if pd.isna(val):
                    continue  # skip missing values entirely

                if end_date not in combined_map:
                    # First time seeing this period → keep it
                    combined_map[end_date] = item.copy()
                else:
                    # Date already present — check if existing val is NaN
                    existing_val = combined_map[end_date]["val"]
                    if pd.isna(existing_val):
                        # Replace NaN with valid fallback value
                        combined_map[end_date]["val"] = val

        # Convert back to list (to match original downstream expectations)
        combined_items = list(combined_map.values())
        
        # Step 4c: Sort by end date descending and limit by periods
        sorted_items = sorted(combined_items, key=lambda x: x["end"], reverse=True)
        metrics[metric] = filter_items_by_years(sorted_items, number_of_years)

    # Step 5: Convert to DataFrame
    df = sec_metrics_to_dataframe(metrics, ticker)

    # Step 6: Apply custom metrics
    df = apply_custom_metrics(df, CUSTOM_METRICS)

    # Step 7: Optional filtering by allowed_periods
    if allowed_periods is not None:
        df = df[df.index.isin(allowed_periods)]

    return df

@lru_cache(maxsize=32)
def build_fiscal_metadata(ticker: str, filing_types: tuple = ("10-K", "10-Q")) -> pd.DataFrame:
    """
    Build a metadata table for a company, listing fiscal period end dates by filing type.

    Parameters
    ----------
    ticker : str
        Stock ticker symbol (e.g., "AAPL").
    filing_types : list of str, default ["10-K", "10-Q"]
        Filing types to include in the table.
    periods : int, default 20
        Maximum number of historical periods to include per filing type.

    Returns
    -------
    pd.DataFrame
        Metadata table with columns: ['ticker', 'filing_type', 'end_date']
    """
    
    # Step 1: Get CIK and SEC data
    cik = get_cik_from_ticker(ticker)
    data = get_sec_submissions(cik)

    forms = data['filings']['recent']['form']
    report_dates = data['filings']['recent']['reportDate']
    filing_dates = data['filings']['recent']['filingDate']
    accession_numbers = data['filings']['recent']['accessionNumber']

    # Step 2: collect all 10-K and 10-Q filings
    all_reports = []

    for idx, form in enumerate(forms):
        if form in filing_types:
            all_reports.append({
                "form": form,
                "report_date": report_dates[idx],
                "filing_date": filing_dates[idx],
                "accession_number": accession_numbers[idx]
            })

    # Step 3: Create DataFrame and sort
    df = pd.DataFrame(all_reports)
    df = df.sort_values("report_date", ascending=False)
    df["symbol"] = ticker
    df["exchange"] = data["exchanges"][0]
    df["name"] = data["name"]
    df["sicDescription"] = data["sicDescription"]
    df["ownerOrg"] = data["ownerOrg"]
    df["cik"] = data["cik"]
    
    return df

if __name__ == "__main__":
    import time
    start_time = time.time()
    
    for ticker in ["MSFT", "NVDA", "META"]:
        # Metadata
        df_metadata = build_fiscal_metadata(ticker) 
        periods_10k = df_metadata.query("form == '10-K'")["report_date"].tolist()
        periods_10q = df_metadata.query("form == '10-Q'")["report_date"].tolist()
        
        # # Fundamentals
        # latest_10k = get_company_metrics_history(ticker, number_of_years=10, filing_type="10-K")
        # latest_10q = get_company_metrics_history(ticker, number_of_years=5, filing_type="10-Q")
        #historical_10q = get_company_metrics_history(ticker, number_of_years=5, filing_type="10-Q")
        historical_10k = get_company_metrics_history(ticker, number_of_years=10, filing_type="10-K")
        
        # Fitler based on metadata
        filtered_historical_10k = historical_10k[historical_10k.index.isin(periods_10k)]
        print(filtered_historical_10k[["Revenue", "LongTermDebt"]])
        
    delta_time = round(time.time() - start_time, 2)
    print("Total time:", delta_time)