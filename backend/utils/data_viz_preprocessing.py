import pandas as pd

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

