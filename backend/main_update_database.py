import time
import pandas as pd
import yfinance as yf 
from itertools import chain
from typing import Dict, List

from utils.pandas_utils import _convert_date_columns, _round_columns
from utils.sec_processing import build_fiscal_metadata, get_cik_from_ticker, get_all_us_gaap_data
from utils.config import CUSTOM_METRICS, METRICS_CONCEPTS, COMPANY_TAG_OVERRIDES, MAX_ANNUAL_DELTA_DAYS, MAX_QUARTER_DELTA_DAYS, MIN_ANNUAL_DELTA_DAYS, MIN_QUARTER_DELTA_DAYS

import logging
logger = logging.getLogger(__name__)

import certifi
import os

os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()

SHARE_METRICS = ["WeightedAverageNumberOfSharesOutstandingBasic", "WeightedAverageNumberOfDilutedSharesOutstanding"]

def get_company_metrics_history(ticker: str, filing_type: str = "10-K") -> pd.DataFrame:
    ticker = ticker.upper()
    
    # Step 1: Get CIK
    cik = get_cik_from_ticker(ticker)
    if not cik:
        raise ValueError(f"Invalid ticker: {ticker}")

    # Step 2: Fetch SEC GAAP data
    sec_data = get_all_us_gaap_data(cik)
    if not sec_data:
        raise RuntimeError(f"Failed to fetch GAAP sec_data for {ticker}")
    
    # Step 2.1: Keep only relevant us:gaap metrics 
    if not sec_data.get("facts", {}).get("us-gaap"):
        return pd.DataFrame()
    
    us_gaap = sec_data["facts"]["us-gaap"]
    relevant_metrics = set(chain(*METRICS_CONCEPTS.values(), *COMPANY_TAG_OVERRIDES.get(ticker, {}).values()))
    us_gaap = {k: v for k, v in us_gaap.items() if k in relevant_metrics}
    
    # Step 3: Preprocess once 
    preprocessed = _preprocess_us_gaap(us_gaap, filing_type)

    # Step 4: Merge metrics 
    df = _merge_sec_metrics(preprocessed, ticker=ticker, metrics_dict=METRICS_CONCEPTS, company_metrics=COMPANY_TAG_OVERRIDES)

    # Clean up missing start date entries with lookup table
    if not {'metric', 'val', 'start', 'end'}.issubset(df.columns):
        return pd.DataFrame()

    # Step 5: Pivot metric column to multiple columns using metric & val columns
    df, pivot_index, frame_dict = _pivot_data_preparation(df, filing_type)
    df = df.pivot_table(index=pivot_index, columns='metric', values='val', aggfunc='first').reset_index()
    df = _round_columns(df, columns=["DilutedEps", "BasicEps"], decimals=2)

    # Step 6: Compute custom metrics
    df = _apply_custom_metrics(df, CUSTOM_METRICS).sort_values("end", ascending=False)
    
    # Step 7: Add additional metadata and data cleaning
    df["form"] = filing_type
    df["ticker"] = ticker
    
    if "frame" not in df.columns:
        df["frame"] = pd.NA
        df["frame"] = df["frame"].fillna(df["end"].map(frame_dict)).fillna("CY" + pd.to_datetime(df["end"], errors='coerce').dt.year.astype(str))
    
    # TODO: Testcase -> per 10-K only 1 entry, no duplicates in frame etc.
    return df

def _merge_sec_metrics(data, ticker, metrics_dict: dict, company_metrics: dict):
    all_dfs = []
    for metric, default_concepts in metrics_dict.items():
        # Step 4a: Determine the ranked list of concepts
        override_list = company_metrics.get(ticker, {}).get(metric, [])
        concepts = override_list + [c for c in default_concepts if c not in override_list]

        # Step 4b: Merge items with fallback ranking
        dfs = []
        for priority, concept in enumerate(concepts):
            df = data.get(concept)
            if df is not None:
                df = df.copy()
                df["priority"] = priority
                if df is not None and not df.empty:
                    dfs.append(df)

        if not dfs:
            continue  # nothing for this metric

        # Vectorized merge with quarter-level alignment
        combined = (pd.concat(dfs, ignore_index=True).sort_values(['end', 'priority']).groupby('end', as_index=False).first().drop(columns=['priority']))

        # Sort and filter by most recent years
        combined["metric"] = metric
        combined = combined.sort_values('end', ascending=False)
        all_dfs.append(combined)

    # Merge metrics to one large dataframe 
    if not all_dfs:
        return pd.DataFrame()  
    df = pd.concat(all_dfs, ignore_index=True)
    
    return df

def _find_missing_quarter_ranges(fy_start: pd.Timestamp, fy_end: pd.Timestamp, group: pd.DataFrame):
    if group.empty:
        return [(fy_start, fy_end)]

    # Ensure datetime
    group = group.copy()
    group = _convert_date_columns(group, columns=["start", "end"])
    
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

def _add_missing_frame(group, missing_start):
    existing_quarters = {frame[-2:] for frame in set(group['frame'].dropna())}
    missing_quarter = {'Q1', 'Q2', 'Q3', 'Q4'} - existing_quarters
    if len(missing_quarter) > 1:
        missing_frame = None
    else:
        missing_frame = f"CY{missing_start.year}{missing_quarter.pop()}"
        
    return missing_frame

def _fix_missing_quarters(df_fundamental, df_fy, metric: str):
    new_rows = []
    
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
        
        # If we have atleast 3 quarters worth of data, we can than fix the single missing frame
        if (MIN_QUARTER_DELTA_DAYS * 3 < total_days) and (total_days < MAX_QUARTER_DELTA_DAYS * 3) and (len(group) < 4):
            if metric in SHARE_METRICS:
                missing_val = fy_val
            else:
                q_sum = group['val'].sum()
                missing_val = fy_val - q_sum

            # Estimate missing quarter’s date range
            missing_fy_dates = _find_missing_quarter_ranges(fy_start, fy_end, group)
            if len(missing_fy_dates) == 1:
                missing_start, missing_end = missing_fy_dates[0]
            else:
                raise ValueError("Unexpected behaviour with function or data '_find_missing_quarter_ranges'.")
                    
            if missing_end > missing_start:
                missing_frame = _add_missing_frame(group, missing_start)
                    
                # Build new row 
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
                new_rows.append(new_row)
    
    if new_rows:
        df_fundamental = pd.concat([df_fundamental, pd.DataFrame(new_rows)], ignore_index=True)
                
    return df_fundamental

def _preprocess_us_gaap(us_gaap: dict, filing_type: str, allowed_units: list = ["USD", "shares", "USD/shares"]) -> Dict[str, List[dict]]:
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
   
        # Load and filter df
        df = pd.DataFrame(units[unit_to_use])
        df = df[df["form"] == "10-K"] if filing_type == "10-K" else df[df["form"].isin(["10-K", "10-Q"])]
        df = _convert_date_columns(df, columns=["start", "end", "filed"])
                
        # Compute delta_days if start & end exists and sort by filing date descending
        if 'start_dt' in df.columns and 'end_dt' in df.columns:
            df['delta_days'] = (df['end_dt'] - df['start_dt']).dt.days
        if 'filed_dt' in df.columns:
            df = df.sort_values(by='filed_dt', ascending=False)

        # Earnings report form selection
        if filing_type == "10-K":        
            if 'delta_days' in df.columns:
                df = df[df['delta_days'].between(MIN_ANNUAL_DELTA_DAYS, MAX_ANNUAL_DELTA_DAYS)]
            df_fundamental = df.drop_duplicates(subset=[c for c in ['start', 'end'] if c in df.columns])
        else:
            if "start" not in df.columns:
                # Drop duplicates based on start/end, keeping the first (latest filed)
                df_fundamental = df.drop_duplicates(subset=["end", "val"]).drop_duplicates(subset=['end'], keep='first')
                
            else:
                # Drop duplicates based on start/end, keeping the first (latest filed)
                df = df.drop_duplicates(subset=['start', 'end'], keep='first')

                # Select single quarters only
                df_fundamental = df[df['delta_days'].between(MIN_QUARTER_DELTA_DAYS, MAX_QUARTER_DELTA_DAYS)]

                # Extend fundamental data using 10-K form to append missing Q4
                df_fy = df[df['delta_days'].between(MIN_ANNUAL_DELTA_DAYS, MAX_ANNUAL_DELTA_DAYS) & (df.form == "10-K")]
                df_fundamental = _fix_missing_quarters(df_fundamental, df_fy, metric=concept)
                
        # Store result to main Dict            
        if not df_fundamental.empty:
            preprocessed[concept] = df_fundamental.sort_values(by='end', ascending=False)
    
    return preprocessed

def _apply_custom_metrics(df: pd.DataFrame, metrics: List[Dict]) -> pd.DataFrame:
    df = df.convert_dtypes()
    
    for metric in metrics:
        cols = metric["columns"]
        func = metric["func"]
        result_col = metric["result_col"]
        drop_inputs = metric.get("drop_inputs", False)

        # Identify missing columns
        missing_cols = [c for c in cols if c not in df.columns]

        if missing_cols:
            # Strict mode: skip optional metrics with missing inputs, fill with NA
            logger.warning(f"Warning: Missing columns for '{result_col}': {missing_cols}. Filling with NA.")
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
    
def _pivot_data_preparation(df, filing_type:str):
    start_dt_dict = df[["start", "end"]].sort_values(by="end", na_position="last").set_index("end").drop_duplicates().dropna()["start"].to_dict()    
    df["start"] = df["start"].fillna(df["end"].map(start_dt_dict)).fillna("1900-01-01")
    
    if "frame" in df.columns:
        df["frame"] = df["frame"].str.replace(r"I$", "", regex=True)
    
    # Init lookup table and pivot index
    frame_dict = {}
    if filing_type == "10-Q": 
        pivot_index = ['start', 'end', 'frame'] 
    else: 
        pivot_index = ['start', 'end'] 
        df["frame"] = df["frame"].str.replace(r"Q\d+$", "", regex=True)
        frame_dict = df[["frame", "end"]].sort_values(by="end", na_position="last").set_index("end").drop_duplicates().dropna()["frame"].to_dict()   
    
    return df, pivot_index, frame_dict
   
def get_market_cap_exact_dates(ticker_symbol: str, dates: pd.DatetimeIndex) -> pd.Series:
    dates = pd.to_datetime(dates)  # ensure datetime
    start_date = dates.min()
    end_date = dates.max()

    ticker = yf.Ticker(ticker_symbol)

    # Fetch shares outstanding once, remove duplicates
    shares_outstanding = (
        ticker.get_shares_full(start=start_date.strftime("%Y-%m-%d"))
        .rename(columns={"SharesOutstanding": "Shares"})
    )
    shares_outstanding.index = pd.to_datetime(shares_outstanding.index)
    shares_outstanding = shares_outstanding[~shares_outstanding.index.duplicated()]

    # Fetch historical prices
    prices = ticker.history(start=start_date, end=end_date, interval="1d")["Close"]

    # Align shares and prices to requested dates using reindex + forward fill
    shares_aligned = shares_outstanding["Shares"].reindex(dates).ffill()
    prices_aligned = prices.reindex(dates).ffill()

    # Compute Market Cap
    market_cap = prices_aligned * shares_aligned
    market_cap.name = "MarketCap"

    return market_cap

if __name__ == "__main__":
    start_time = time.time()
    
    # Arguments
    mode = "10-Q"
    tickers = ["AAPL","MSFT", "NVDA", "META"]
    
    dfs = []
    for ticker in tickers:
        ticker_start_time = time.time()
        
        # Metadata
        df_metadata = build_fiscal_metadata(ticker) 
        
        # Annual data
        if mode == "10-K":       
            df = get_company_metrics_history(ticker, filing_type="10-K")
        
        # Quarterly data
        elif mode == "10-Q":    
            df = get_company_metrics_history(ticker, filing_type="10-Q")
        
        else:
            raise KeyError(f"Argument 'mode'={mode} not in ['10-Q', '10-K'].")

        # Append results
        dfs.append(df)
        logger.info(f"{ticker} processed in {time.time() - ticker_start_time:.2f}s")
    
    logger.info(f"Total time: {time.time() - start_time:.2f}s.")