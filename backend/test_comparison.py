import numpy as np
import pandas as pd
from pandas.api.types import is_numeric_dtype

from utils.config.logging import init_logger
from utils.config.config import METRICS_CONCEPTS_OLD
from backend.parsers.yahoo_processing import fetch_financials
from main_update_database import get_company_metrics_history, _get_us_gaap_metrics_for_ticker

# Initialize logger
logger = init_logger(name=__name__, level="INFO", log_file="logs/app.log")

def _make_slices_softmatch(yf_df: pd.DataFrame, sec_df: pd.DataFrame, max_rows=None, tolerance_days: int = 30):
    """
    Create aligned YF and SEC slices using nearest-date soft matching on 'end' column.
    Returns: yf_slice, sec_slice, merged
    """
    if "end" not in yf_df.columns or "end" not in sec_df.columns:
        raise ValueError("Both dataframes must contain an 'end' column for soft matching.")

    yf_df = yf_df.copy()
    sec_df = sec_df.copy()

    yf_df["end"] = pd.to_datetime(yf_df["end"])
    sec_df["end"] = pd.to_datetime(sec_df["end"])
    yf_df = yf_df.sort_values("end").reset_index(drop=True)
    sec_df = sec_df.sort_values("end").reset_index(drop=True)

    merged = pd.merge_asof(
        yf_df.rename(columns={"end": "end_yf"}),
        sec_df.rename(columns={"end": "end_sec"}),
        left_on="end_yf",
        right_on="end_sec",
        direction="nearest",
        tolerance=pd.Timedelta(days=tolerance_days),
        suffixes=("_yf", "_sec"),
    )

    merged = merged.dropna(subset=["end_sec"])
    merged["date_diff_days"] = (merged["end_yf"] - merged["end_sec"]).dt.days.abs()

    yf_slice = merged[[c for c in merged.columns if c.endswith("_yf")]]
    sec_slice = merged[[c for c in merged.columns if c.endswith("_sec")]]
    
    # Clean column names back to original
    yf_slice.columns = [c.replace("_yf", "") for c in yf_slice.columns]
    sec_slice.columns = [c.replace("_sec", "") for c in sec_slice.columns]

    if max_rows is not None:
        yf_slice = yf_slice.iloc[:max_rows]
        sec_slice = sec_slice.iloc[:max_rows]

    return yf_slice, sec_slice, merged

def compare_yfinance_to_sec_extended(yf_df: pd.DataFrame, sec_df: pd.DataFrame, key_cols=None, max_rows=None):
    # --- Create slices using soft date matching ---
    yf_slice, sec_slice, merged = _make_slices_softmatch(yf_df, sec_df, max_rows=max_rows)

    # Determine columns to compare
    if key_cols is None:
        key_cols = list(set(yf_df.columns) & set(sec_df.columns))
        if "end" in key_cols:
            key_cols.remove("end")

    n_rows = len(yf_slice)
    report_rows = []

    for col in key_cols:
        yf_values = yf_slice[col] if col in yf_slice else pd.Series([pd.NA]*n_rows)
        sec_values = sec_slice[col] if col in sec_slice else pd.Series([pd.NA]*n_rows)

        # Mismatches
        mismatches_mask = (yf_values != sec_values) & ~(yf_values.isna() & sec_values.isna())
        num_mismatches = mismatches_mask.sum()
        mismatch_pct = (num_mismatches / n_rows) * 100 if n_rows else 0
        mismatches_str = f"{num_mismatches} mismatches ({round(mismatch_pct, 1)}%)" if num_mismatches > 0 else "OK"

        # Data type mismatch
        type_mismatch = any([type(y) != type(s) for y, s in zip(yf_values, sec_values) if pd.notna(y) and pd.notna(s)])
        type_mismatch_str = "Data type mismatch" if type_mismatch else "OK"

        # NaN vs zero mismatch
        nan_zero_mismatch = not ((yf_values.fillna(0) == 0) & (sec_values.fillna(0) == 0)).all()
        nan_zero_mismatch_str = "NaN/zero mismatch" if nan_zero_mismatch else "OK"

        # Percent difference for numeric columns
        percent_diff = pd.NA
        if is_numeric_dtype(yf_values) and is_numeric_dtype(sec_values):
            with np.errstate(divide='ignore', invalid='ignore'):
                diff = np.abs(yf_values - sec_values)
                percent_diff = (diff / sec_values.replace({0: np.nan})) * 100
                percent_diff = percent_diff.mean(skipna=True)

        # Overall issue boolean
        overall_issue = num_mismatches > 0 or type_mismatch or nan_zero_mismatch

        report_rows.append({
            "metric": col,
            "mismatches": mismatches_str,
            "type_mismatch": type_mismatch_str,
            "nan_zero_mismatch": nan_zero_mismatch_str,
            "avg_percent_diff": round(percent_diff, 2) if pd.notna(percent_diff) else pd.NA,
            "overall_issue": overall_issue
        })

    report = pd.DataFrame(report_rows)
    
    return report

def mismatches_helper(yf_df: pd.DataFrame, sec_df: pd.DataFrame, comparison_report: pd.DataFrame, key_cols=None, max_rows=None):
    """
    Create a helper DataFrame showing only the mismatches with YFinance and SEC values.
    Handles pd.NA properly.
    """
    # --- Create slices using soft date matching ---
    yf_slice, sec_slice, merged = _make_slices_softmatch(yf_df, sec_df, max_rows=max_rows)

    if key_cols is None:
        key_cols = list(set(yf_df.columns) & set(sec_df.columns))
        if 'end' in key_cols:
            key_cols.remove('end')
 
    n_rows = len(yf_slice)
    mismatched_metrics = comparison_report[comparison_report['overall_issue'] == True]['metric'].tolist()

    rows = []
    for metric in mismatched_metrics:
        if metric not in key_cols:
            continue
        for i in range(n_rows):
            yf_val = yf_slice.at[i, metric] if metric in yf_slice else pd.NA
            sec_val = sec_slice.at[i, metric] if metric in sec_slice else pd.NA
            frame_val = yf_slice.at[i, 'frame'] if 'frame' in yf_slice else pd.NA

            # Handle pd.NA safely
            yf_isna = pd.isna(yf_val)
            sec_isna = pd.isna(sec_val)
            values_differ = (yf_val != sec_val) if not (yf_isna or sec_isna) else (yf_isna != sec_isna)

            if values_differ:
                rows.append({
                    "metric": metric,
                    "row": i,
                    "yf_value": yf_val,
                    "sec_value": sec_val,
                    "frame": frame_val,
                    "symbol": yf_slice.ticker.iloc[i],
                    "end_yf": yf_slice.end.iloc[i],
                    "end_sec": sec_slice.end.iloc[i],
                })

    helper_df = pd.DataFrame(rows)
    return helper_df

def map_yf_to_sec_metrics(yf_df: pd.DataFrame, sec_preprocessed: dict, helper_df: pd.DataFrame, candidates: dict = None, key_date_col="end"):
    results = []

    # Ensure date is datetime
    yf_df = yf_df.copy()
    yf_df[key_date_col] = pd.to_datetime(yf_df[key_date_col])
    mismatching_columns = helper_df.metric.unique()
    
    for yf_metric in mismatching_columns:
        if yf_metric in ["ticker", "form", "frame", "GrossProfit"]:
            continue  # skip metadata

        # Get candidates
        gaap_candidates = candidates.get(yf_metric, list(sec_preprocessed.keys())) if candidates else [item for item in list(sec_preprocessed.keys()) if yf_metric.lower() in item.lower()]
        best_metric = None
        best_diff = np.inf
        best_aligned = 0

        yf_series = yf_df[[key_date_col, yf_metric]].dropna()

        # TODO: Option 1: Check over our tag array and hopefully there is a match VS if no 100% accuracy with yfinance we can calculate it on our own (partial observation of test report analysis)
        for gaap_metric in gaap_candidates:
            if gaap_metric not in sec_preprocessed:
                continue

            sec_series = sec_preprocessed[gaap_metric][["end_dt", "val"]].dropna()
            if sec_series.empty:
                continue

            # Merge on dates
            merged = pd.merge(yf_series, sec_series, left_on=key_date_col, right_on="end_dt", how="inner", suffixes=("_yf", "_sec"))
            if merged.empty:
                continue

            # Compute percent differences
            with np.errstate(divide='ignore', invalid='ignore'):
                diff = np.abs(merged[f"{yf_metric}"] - merged["val"])
                pct_diff = (diff / merged["val"].replace({0: np.nan})) * 100
                avg_diff = pct_diff.mean(skipna=True)

            if avg_diff < best_diff:
                best_diff = avg_diff
                best_metric = gaap_metric
                best_aligned = len(merged)

        results.append({
            "yf_metric": yf_metric,
            "best_gaap_metric": best_metric if best_metric else pd.NA,
            "avg_percent_diff": round(best_diff, 2) if best_metric else pd.NA,
            "num_aligned_quarters": best_aligned
        })

    return pd.DataFrame(results)

# Example usage
if __name__ == "__main__":
    filing_type="10-K"
    tickers = ["V"] # ["AAPL", "NVDA", "MSFT", "AMZN", "V", "FICO", "ADBE", "ANET", "GOOGL"]
    
    for symbol in tickers:        
        logger.info(f"[{symbol}] Fetching from YFinance data...")
        df_yf = fetch_financials(symbol, quarterly=(filing_type=="10-Q"))

        logger.info(f"[{symbol}] Fetching from SEC EDGAR data...")
        df_sec = get_company_metrics_history(symbol, filing_type=filing_type)

        logger.info(f"[{symbol}] Compared SEC with Yahoo")
        comparison_report = compare_yfinance_to_sec_extended(df_yf, df_sec)
        helper_df = mismatches_helper(df_yf, df_sec, comparison_report)
        
        logger.info(f"[{symbol}] Searching better metric...")
        #sec_preprocessed = _get_us_gaap_metrics_for_ticker(symbol, filing_type=filing_type)
        metrics_map = map_yf_to_sec_metrics(yf_df=df_yf, sec_preprocessed=df_sec, helper_df=helper_df, candidates=METRICS_CONCEPTS_OLD)
        logger.info(f"[{symbol}] Finished better metric search")

# TODO: Calc GrossProfit if not exist as Revenue - COGS, Example AMZN
# TODO: For McDonalds shares outstanding issues. Need to multiply with 1mio...
# TODO: Calc OperatingIncome with formula for J&J 1)Operating Income=Gross Profit−Operating Expenses 2)Operating Income=Net Income+Interest Expense+Tax Expense±Other Non-Operating Items