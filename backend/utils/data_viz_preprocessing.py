import datetime
import pandas as pd

from utils.config.logging import init_logger
from utils.math_utils import safe_typecast, format_currency
from utils.date_utils import safe_strftime, delta_hours_from_date

logger = init_logger(name=__name__, level="DEBUG", log_file="logs/app.log")

def build_table_json(df, columns: list):
    existing_cols = [c for c in columns if c in df.columns]
    return df[existing_cols].to_dict(orient="records")

def build_eps_scatter_series(df: pd.DataFrame):
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
            performance[period][key] = safe_typecast(latest[col], "float")

    # Delta hours calculation
    now = datetime.datetime.now()
    delta_hours = delta_hours_from_date(now, latest.get("lastUpdated"))
    isLive = False
    if delta_hours is not None:
        isLive = delta_hours <= 1 # We are live when latest stock price value was not olde than 1 Hour
    
    return {
        "currentPrice": safe_typecast(latest.get("currentPrice"), "float"),
        "relChange": safe_typecast(latest.get("relChange"), "float"),
        "absChange": safe_typecast(latest.get("absChange"), "float"),
        "lastUpdated": safe_strftime(latest.get("lastUpdated")),
        "isLive": isLive,
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
                    {"name": "Market Capitalization", "value": format_currency(round(float(latest.marketCap)))},
                    {"name": "P/E Ratio (TTM/FWD)", "value": f"{float(latest.pe_trailing)} | {float(latest.pe_forward)}"},
                    {"name": "P/B & P/S Ratio", "value": f"{float(latest.pb)} | {float(latest.ps)}"},
                    {"name": "EV/EBITDA", "value": float(latest.ev_ebitda)}
                ]
            },
            {
                "title": "Cash Flow",
                "kpis": [
                    {"name": "FCF Per Share (Yield | Yield w/o SBC)", "value": format_currency(int(latest.freeCashflow))},
                    {"name": "OCF Per Share (Yield)", "value": None},
                    {"name": "Total Cash & Debt (Ratio)", "value": f"{format_currency(int(latest.totalCash))} | {format_currency(int(latest.totalDebt))} ({float(latest.cashDebtRatio)})"},
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

def build_historical_earnings_data(df: pd.DataFrame):
    if df.empty:
        return {}

    result = []
    for _, row in df.iterrows():
        # Convert Timestamp to string
        date_str = row['date'].strftime('%Y-%m-%d') if not pd.isna(row['date']) else None

        # EPS values
        eps_estimate = float(row['epsEstimate']) if not pd.isna(row['epsEstimate']) else None
        eps_reported = float(row['epsReported']) if not pd.isna(row['epsReported']) else None
        eps_delta = float(row['epsDelta']) if 'epsDelta' in row and not pd.isna(row['epsDelta']) else None

        # Revenue values - if your DF has no revenue, we can leave as None or mock
        revenue_estimate = None
        revenue_reported = None
        revenue_delta = None

        result.append({
            'date': date_str,
            'epsEstimate': eps_estimate,
            'epsReported': eps_reported,
            'epsDelta': eps_delta,
            'revenueEstimate': revenue_estimate,
            'revenueReported': revenue_reported,
            'revenueDelta': revenue_delta,
            'secFiling': row['sec_filing'] if 'sec_filing' in row and pd.notna(row['sec_filing']) else None
        })

    return result

def build_next_earnings_data(df: pd.DataFrame):
    if df.empty:
        return {}
    
    row = df.iloc[0]  # take first row for next earnings

    # Convert dates to string if they are Timestamps
    next_earnings_date = (
        row['nextEarningsDate'].strftime('%Y-%m-%d') 
        if isinstance(row['nextEarningsDate'], pd.Timestamp) else str(row['nextEarningsDate'])
    )
    dividend_ex_date = (
        row['dividendExDate'].strftime('%Y-%m-%d') 
        if isinstance(row['dividendExDate'], pd.Timestamp) else str(row['dividendExDate'])
    )

    result = {
        'date': next_earnings_date,
        'epsEstimate': float(row['epsEstimate']) if pd.notna(row['epsEstimate']) else None,
        'revenueEstimate': None,  # placeholder if revenue not available
        'dividendExDate': dividend_ex_date,
        'expectedDividend': float(row['expectedDividend']) if pd.notna(row['expectedDividend']) else None
    }

    return result

def _build_scatter_series(df: pd.DataFrame, value_col: str, title: str, color: str):
    if df.empty or value_col not in df.columns:
        return {"name": title, "data": [], "color": color}

    # Helper to convert date to "YYYY Qx" format
    def date_to_quarter(date):
        if pd.isna(date):
            return None
        month = date.month
        quarter = (month - 1) // 3 + 1
        return f"{date.year} Q{quarter}"
    
    df = df.sort_values('date', ascending=True)
    
    series_data = []
    for _, row in df.iterrows():
        quarter_label = date_to_quarter(row['date'])
        if quarter_label is None:
            continue
        value = float(row[value_col]) if pd.notna(row[value_col]) else None
        series_data.append([quarter_label, value])

    return {
        "name": title,
        "data": series_data,
        "color": color
    }

def build_eps_scatter_series(df):
    eps_est_series = _build_scatter_series(df, "epsEstimate", "EPS Estimate", "#6AD396")
    eps_act_series = _build_scatter_series(df, "epsReported", "EPS Actual", "#4F46E5")

    scatter_series = [eps_est_series, eps_act_series]
    return scatter_series

def get_earnings_columns():
    return [
        {"key": "date", "name": "Date"},
        {"key": "epsReported", "name": "EPS Reported", "format": "currency"},
        {"key": "epsEstimate", "name": "EPS Estimate", "format": "currency"},
        {"key": "epsDelta", "name": "EPS Δ", "format": "deltaTag"}
    ]