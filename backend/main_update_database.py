import time
import pandas as pd 
from functools import lru_cache
from typing import Optional, Dict, List

from utils.sec_processing import build_fiscal_metadata, safe_request, get_cik_from_ticker, CACHE_SIZE

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

def find_missing_quarter_ranges(fy_start: pd.Timestamp, fy_end: pd.Timestamp, group: pd.DataFrame):
    if group.empty:
        return [(fy_start, fy_end)]

    # Ensure datetime
    group = group.copy()
    group["start_dt"] = pd.to_datetime(group["start_dt"])
    group["end_dt"] = pd.to_datetime(group["end_dt"])

    # Sort by start date
    group = group.sort_values("start_dt").reset_index(drop=True)

    missing = []

    # 1️⃣ Missing before the first available quarter
    first_start = group["start_dt"].iloc[0]
    if first_start > fy_start:
        missing.append((fy_start, first_start - pd.Timedelta(days=1)))

    # 2️⃣ Missing gaps between known quarters
    for i in range(len(group) - 1):
        prev_end = group["end_dt"].iloc[i]
        next_start = group["start_dt"].iloc[i + 1]

        # If there's a non-contiguous gap
        if next_start > prev_end + pd.Timedelta(days=1):
            missing.append((prev_end + pd.Timedelta(days=1), next_start - pd.Timedelta(days=1)))

    # 3️⃣ Missing after the last known quarter
    last_end = group["end_dt"].iloc[-1]
    if last_end < fy_end:
        missing.append((last_end + pd.Timedelta(days=1), fy_end))

    return missing

def preprocess_us_gaap(us_gaap: dict, filing_type: str, allowed_units: list = ["USD", "shares", "USD/shares"], use_frames: bool = True,) -> Dict[str, List[dict]]:
    """
    Preprocess US GAAP data for a given filing type.
    Returns a dict: concept -> list of items with 'end' and 'val'.
    """
    #TODO: I loop here overall concepts in the report, but i could already filter out units maybe efficiently with a one-liner or to save space pre-select the relevant metrics already!
    preprocessed = {}
    
    for concept, concept_data in us_gaap.items():
        units = concept_data.get("units", {})
        unit_to_use = next((u for u in allowed_units if u in units), None)
  
        if not unit_to_use:
            continue
        
        if concept == "AssetsCurrent":
            a=0
      
        if filing_type == "10-K":
            #filtered_items = [i for i in units[unit_to_use] if i.get("form") == filing_type and "val" in i and "end" in i]
            df_fundamental = pd.DataFrame(units[unit_to_use])
            df_fundamental = df_fundamental[df_fundamental.form == "10-K"]
            
            # Convert 'start' and 'end' to datetime
            if ('start' in df_fundamental.columns) and ('end' in df_fundamental.columns):
                df_fundamental['start_dt'] = pd.to_datetime(df_fundamental['start'])
                df_fundamental['end_dt'] = pd.to_datetime(df_fundamental['end'])
                df_fundamental['delta_days'] = (df_fundamental['end_dt'] - df_fundamental['start_dt']).dt.days
                df_fundamental = df_fundamental[(df_fundamental['delta_days'] >= 330) & (df_fundamental['delta_days'] <= 390)]
            
            # Drop duplicates on columns that exist
            cols_to_check = [c for c in ['start', 'end'] if c in df_fundamental.columns]
            df_fundamental['filed_dt'] = pd.to_datetime(df_fundamental['filed'], errors='coerce')
            df_fundamental = df_fundamental.sort_values(by='filed_dt', ascending=False)
            df_fundamental = df_fundamental.drop_duplicates(subset=cols_to_check)    

        else:
            # TODO: Fetch quarterly results and the missing Q4
            df = pd.DataFrame(units[unit_to_use])
            df = df[df["form"].isin(["10-K", "10-Q"])]
            
            if not "start" in df.columns:
                #TODO: Extend and check this again e.g. frame handling and make eveything more readable, robust and i think after fixing the custom metrics we can work on coss-checking with other tools and than stoer the results long-term as partitioned files
                df_fundamental = df.drop_duplicates(subset=["end", "val"]).sort_values(by='end', ascending=False)
                
                # Drop duplicates
                df_fundamental['filed_dt'] = pd.to_datetime(df_fundamental['filed'], errors='coerce')
                # Sort by filing date descending (latest first)
                df_fundamental = df_fundamental.sort_values(by='filed_dt', ascending=False)

                # Drop duplicates based on start/end, keeping the first (latest filed)
                df_fundamental = df_fundamental.drop_duplicates(subset=['end'], keep='first')
                
                # Test case
                df_fundamental['end_year'] = pd.to_datetime(df_fundamental['end'], errors='coerce').dt.year
                if df_fundamental.value_counts("end_year").max() > 4:
                    a=0
            else:
                # Convert 'start' and 'end' to datetime
                df['start_dt'] = pd.to_datetime(df['start'])
                df['end_dt'] = pd.to_datetime(df['end'])
                df['delta_days'] = (df['end_dt'] - df['start_dt']).dt.days
                
                # Drop duplicates
                df['filed_dt'] = pd.to_datetime(df['filed'], errors='coerce')

                # Sort by filing date descending (latest first)
                df = df.sort_values(by='filed_dt', ascending=False)

                # Drop duplicates based on start/end, keeping the first (latest filed)
                df = df.drop_duplicates(subset=['start', 'end'], keep='first')

                # Get quarters
                df_fundamental = df[(df['delta_days'] >= 80) & (df['delta_days'] <= 100)]
                #df_fundamental = df_fundamental.drop_duplicates(["start", "end", "val"])
                
                # Edit df
                df_fy = df[(df['delta_days'] >= 330) & (df['delta_days'] <= 390)]
                df_fy = df_fy[df_fy.form == "10-K"]#.drop_duplicates(["start", "end", "val"])
                
            
                # Fix missing quarter
                for _, fy_row in df_fy.iterrows():
                    fy_start = fy_row['start_dt']
                    fy_end = fy_row['end_dt']
                    fy_val = fy_row['val']

                    # Filter quarterly entries that fall fully inside this fiscal year
                    group = df_fundamental[(df_fundamental['end_dt'] <= fy_end) & (df_fundamental['start_dt'] >= fy_start)]

                    if group.empty:
                        continue  # no data for that FY

                    # Check for missing quarter (roughly < 4 quarters worth of days)
                    total_days = group.delta_days.sum()
                    
                    if (240 < total_days) and (total_days < 300) and (len(group) < 4):
                        q_sum = group['val'].sum()
                        missing_val = fy_val - q_sum

                        # Estimate missing quarter’s date range
                        missing_fy_dates = find_missing_quarter_ranges(fy_start, fy_end, group)
                        if len(missing_fy_dates) == 1:
                            missing_start, missing_end = missing_fy_dates[0]
                        else:
                            raise ValueError("Unexpected behaviour with function or data 'find_missing_quarter_ranges'.")
                                
                        if missing_end > missing_start:
                            existing_quarters = {frame[-2:] for frame in set(group['frame'].dropna())}
                            missing_quarter = {'Q1', 'Q2', 'Q3', 'Q4'} - existing_quarters
                            if len(missing_quarter) > 1:
                                missing_frame = None
                            else:
                                missing_frame = f"CY{missing_start.year}{missing_quarter.pop()}"
                                
                            #TODO: add other missing data to new_row dict
                            new_row = {
                                'start': missing_start.strftime('%Y-%m-%d'),
                                'end': missing_end.strftime('%Y-%m-%d'),
                                'val': missing_val,
                                'fy': fy_row.fy,
                                'start_dt': missing_start,
                                'end_dt': missing_end,
                                'form': "10-Q",
                                'frame': missing_frame
                            }
                            
                            # Add it using concat
                            df_fundamental = pd.concat([df_fundamental, pd.DataFrame([new_row])], ignore_index=True)
                        
        if not df_fundamental.empty:
            if "end_year" not in df_fundamental.columns:
                df_fundamental['end_year'] = pd.to_datetime(df_fundamental['end'], errors='coerce').dt.year
                
            preprocessed[concept] = df_fundamental.sort_values(by='end', ascending=False)
    
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
def get_company_metrics_history(ticker: str, filing_type: str = "10-K") -> pd.DataFrame:
    # Step 1: Get CIK
    cik = get_cik_from_ticker(ticker)
    if not cik:
        raise ValueError(f"Invalid ticker: {ticker}")

    # Step 2: Fetch SEC GAAP data
    data = get_all_us_gaap_data(cik)
    if not data:
        raise RuntimeError(f"Failed to fetch GAAP data for {ticker}")
    
    # Step 2.1: Keep only relevant us:gaap metrics 
    us_gaap = data["facts"]["us-gaap"]
    relevant_metrics = set(val for sublist in METRICS_CONCEPTS.values() for val in sublist) # TODO: add COMPANY_TAG_OVERRIDES.get(ticker.upper(), {}) to process only the relevant metrics!!!
    us_gaap = {k: v for k, v in us_gaap.items() if k in relevant_metrics}
    
    # Step 3: Preprocess once 
    preprocessed = preprocess_us_gaap(us_gaap, filing_type)

    # Step 4: Merge metrics 
    # TODO: preprocessed is a dict of dataframes now!!!! Fix all rest
    all_dfs = []
    for metric, default_concepts in METRICS_CONCEPTS.items():
        # Step 4a: Determine the ranked list of concepts
        override_list = COMPANY_TAG_OVERRIDES.get(ticker.upper(), {}).get(metric, [])
        concepts = override_list + [c for c in default_concepts if c not in override_list]

        # Step 4b: Merge items with fallback ranking
        dfs = []
        for priority, concept in enumerate(concepts):
            df = preprocessed.get(concept)
            if df is not None:
                df = df.copy()
                df["priority"] = priority
                if df is not None and not df.empty:
                    dfs.append(df)

        if not dfs:
            continue  # nothing for this metric

        # ✅ Efficient vectorized merge with quarter-level alignment
        combined = (
            pd.concat(dfs, ignore_index=True)
              .sort_values(['end', 'priority'])
              .groupby('end', as_index=False)
              .first()  # take top-priority row per quarter
              .drop(columns=['priority'])
        )

        # Sort and filter by most recent years
        combined["metric"] = metric
        combined = combined.sort_values('end', ascending=False)
        all_dfs.append(combined)
        if combined.value_counts("end_year").max() > 4:
            print("Shouldnt happen that we got more than fou entries for a 10-Q!")
    
    # Merge metrics to one large dataframe 
    df = pd.concat(all_dfs)
    df = df.pivot_table(
        index=['start', 'end', 'frame'],  # columns to keep as-is
        columns='metric',                     # column names become metrics
        values='val',                            # values to fill in
        aggfunc='first'                          # take the first non-null if duplicates
    ).reset_index()
    
    # Compute custom metrics
    df = apply_custom_metrics(df, CUSTOM_METRICS).sort_values("end", ascending=False)
    
    # TODO: Add other metadata
    df["form"] = filing_type
    df["ticker"] = ticker
    
    return df
    
    #    combined_map = {}  # key = end date, value = {"end": date, "val": value}
    #     for concept in concepts:
    #         if concept not in preprocessed:
    #             continue
            
    #         root_df = align_to_quarter(concept)
            
    #         # TODO: item now is a DF
    #         for idx, item in preprocessed[concept].iterrows():
    #             end_date = item["end"]
    #             val = item["val"]

    #             if pd.isna(val):
    #                 continue  # skip missing values entirely

    #             if end_date not in combined_map:
    #                 # First time seeing this period → keep it
    #                 combined_map[end_date] = item.copy()
    #             else:
    #                 # Date already present — check if existing val is NaN
    #                 existing_val = combined_map[end_date]["val"]
    #                 if pd.isna(existing_val):
    #                     # Replace NaN with valid fallback value
    #                     combined_map[end_date]["val"] = val

    #     # Convert back to list (to match original downstream expectations)
    #     combined_items = list(combined_map.values())
        
    #     # Step 4c: Sort by end date descending and limit by periods
    #     sorted_items = sorted(combined_items, key=lambda x: x["end"], reverse=True)
    #     metrics[metric] = filter_items_by_years(sorted_items, number_of_years)

    # # Step 5: Convert to DataFrame
    # df = sec_metrics_to_dataframe(metrics, ticker)

    # Step 6: Apply custom metrics
   # df = apply_custom_metrics(df, CUSTOM_METRICS)

    # Step 7: Optional filtering by allowed_periods
    # if allowed_periods is not None:
    #     df = df[df.index.isin(allowed_periods)]

   


if __name__ == "__main__":
    start_time = time.time()
    
    # Arguments
    mode = "10-Q"
    tickers = ["AAPL","MSFT", "NVDA", "META"]
    
    for ticker in tickers:
        # Metadata
        df_metadata = build_fiscal_metadata(ticker) 
        
        # Annual data
        if mode == "10-K":       
            #periods_10k = df_metadata.query("form == '10-K'")["report_date"].tolist()
            df_fundamentals = get_company_metrics_history(ticker, filing_type="10-K")
            #df_fundamentals = historical_10k[historical_10k.index.isin(periods_10k)]
        
        # Quarterly data
        elif mode == "10-Q":    
            #periods_10q = df_metadata.query("form == '10-Q'")["report_date"].tolist()
            df_fundamentals = get_company_metrics_history(ticker, filing_type="10-Q")
            #df_fundamentals = historical_10q[historical_10q.index.isin(periods_10q)]
        
        else:
            raise KeyError(f"Argument 'mode'={mode} not in ['10-Q', '10-K'].")

        # Print
        print(df_fundamentals)
        
    delta_time = round(time.time() - start_time, 2)
    print("Total time:", delta_time)