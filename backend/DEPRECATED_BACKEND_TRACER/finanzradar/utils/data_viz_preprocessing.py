import pandas as pd

from utils.config.logging import init_logger
from utils.pandas_utils import make_df_json_safe
logger = init_logger(name=__name__, level="DEBUG", log_file="logs/app.log")

def build_table_json(df, columns: list):
    existing_cols = [c for c in columns if c in df.columns]
    return df[existing_cols].to_dict(orient="records")

def build_eps_scatter_series(df: pd.DataFrame):
    #import json
    #mock_series = build_eps_scatter_series(df_eps)
    #print(json.dumps(mock_series, indent=2))
    
    # Ensure 'date' is datetime
    df["date"] = pd.to_datetime(df["date"])

    # Sort chronologically (oldest first)
    df = df.sort_values("date")

    # Map month to quarter label
    df["quarter"] = df["date"].apply(lambda dt: f"{dt.year} Q{((dt.month-1)//3)+1}") #TODO use generic function here 

    # Build EPS Estimate series
    eps_estimate_series = {
        "name": "EPS Estimate",
        "data": df[["quarter", "epsEstimate"]].values.tolist(),
        "color": "#F59E0B"
    }

    # Build EPS Actual series
    eps_actual_series = {
        "name": "EPS Actual",
        "data": df[["quarter", "epsReported"]].values.tolist(),
        "color": "#EF4444"
    }

    return [eps_estimate_series, eps_actual_series]

def build_stock_info_data(df: pd.DataFrame):
    """
    Transform a DataFrame filtered for a single ticker (multiple rows possible)
    into nested dict format for the Vue app.
    Picks the latest row based on 'lastUpdated'.
    """
    if df.empty:
        return {}

    # Ensure lastUpdated is datetime
    df["lastUpdated"] = pd.to_datetime(df["lastUpdated"])

    # Take the latest row
    latest = df.sort_values("lastUpdated", ascending=False).iloc[0]

    # Build performance dynamically
    performance = {
        col.replace("performance_", "").replace("_rel", "").replace("_abs", ""): {}
        for col in df.columns if col.startswith("performance_")
    }

    for col in df.columns:
        if col.startswith("performance_"):
            period, kind = col.replace("performance_", "").split("_")
            key = "relStockPriceChange" if kind == "rel" else "absStockPriceChange"
            performance[period][key] = latest[col]

    return {
        "currentPrice": latest.get("currentPrice"),
        "relChange": latest.get("relChange"),
        "absChange": latest.get("absChange"),
        "lastUpdated": latest.get("lastUpdated").isoformat(),
        "isLive": False,
        "performance": performance,
        "industry": latest.get("industry", "N/A"),
        "sector": latest.get("sector", "N/A"),
        "country": latest.get("country", "N/A")
    }

def build_fundamental_data(df: pd.DataFrame, ticker: str, filing_type: str, unit="USD"):
    date_col = "end"
    df = df.sort_values(date_col)
    
    # Non-metric columns to exclude
    non_metric_cols = {"start", "end", "frame"}

    metrics = {}
    for col in df.columns:
        if col in non_metric_cols:
            continue

        values = df[col].tolist()
        dates = df[date_col].tolist()

        # Filter out NaNs and align dates
        filtered_dates = []
        filtered_values = []
        for d, v in zip(dates, values):
            if pd.notna(v):
                filtered_dates.append(d)
                filtered_values.append(v)

        metrics[col] = {"dates": filtered_dates, "values": filtered_values}

    return {
        "ticker": ticker,
        "unit": unit,
        "frequency": "quarterly" if filing_type == "10-Q" else "yearly",
        "metrics": metrics
    }

def build_stock_kpi_groups(df: pd.DataFrame):
    if df.empty:
        return {}
    
    # TODO: Latest selection doesnt make sense right now
    latest = df.iloc[0]
    groups = [
            {
                "title": "Valuation",
                "kpis": [
                    {"name": "Market Capitalization", "value": round(float(latest.marketCap))},
                    {"name": "P/E Ratio (TTM/FWD)", "value": f"{float(latest.pe_trailing)} | {float(latest.pe_forward)}"},
                    {"name": "P/B & P/S Ratio", "value": f"{float(latest.pb)} | {float(latest.ps)}"},
                    {"name": "EV/EBITDA", "value": float(latest.ev_ebitda)}
                ]
            },
            {
                "title": "Cash Flow",
                "kpis": [
                    {"name": "FCF Per Share (Yield | Yield w/o SBC)", "value": int(latest.freeCashflow)},
                    {"name": "OCF Per Share (Yield)", "value": float(latest.cashDebtRatio)},
                    {"name": "Total Cash & Debt (Ratio)", "value": f"{int(latest.totalCash)} | {int(latest.totalDebt)} ({float(latest.cashDebtRatio)})"},
                    {"name": "Debt-to-FCF", "value": float(latest.debtToFCF)}
                ]
            },
            {
                "title": "Margins",
                "kpis": [
                    {"name": "Gross Margin", "value": float(latest.grossMargin)},
                    {"name": "Operating Margin", "value": float(latest.operatingMargin)},
                    {"name": "Net Margin", "value": float(latest.netMargin)},
                    {"name": "FCF & OCF Margin", "value": None}  # placeholder
                ]
            },
            {
                "title": "Growth",
                "kpis": [
                    {"name": "Revenue Growth (YoY)", "value": float(latest.revenueGrowth)},
                    {"name": "Net Income Growth (YoY)", "value": float(latest.earningsGrowth)},
                    {"name": "FCF Growth (YoY)", "value": None},  # placeholder
                    {"name": "ROCE & ROIC", "value": f"{float(latest.roce)} | {float(latest.roic)}"}
                ]
            },
            {
                "title": "Dividend & Earnings",
                "kpis": [
                    {"name": "EPS (TTM|FWD)", "value": f"{float(latest.trailingEPS)} | {float(latest.forwardEPS)}"},
                    {"name": "Earnings Date", "value": latest.nextEarningsDate},
                    {"name": "Dividend Yield & Payout Ratio", "value": f"{float(latest.dividendYield)} | {float(latest.payoutRatio)}"},
                    {"name": "Ex-Dividend & Payout date", "value": f"{latest.exDividendDate} | {latest.payoutDate}"}
                ]
            }
        ]

    return groups
