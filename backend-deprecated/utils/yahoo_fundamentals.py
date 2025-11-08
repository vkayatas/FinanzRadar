import pandas as pd
import yfinance as yf

def fetch_apple_financials(symbol:str, latest: bool = False):
    """
    Fetches Apple (AAPL) financial data from Yahoo Finance in a structured format.
    
    Args:
        latest (bool): If True, returns only the latest values. If False, returns historical series.
    
    Returns:
        dict: Dictionary containing Revenue, OperatingCashFlow, CapitalExpenditures,
              TotalDebt, and FreeCashFlow with date/value pairs.
    """
    ticker = yf.Ticker(symbol)
    
    # Financial statements
    financials = ticker.financials.T         # Income statement (annual)
    cashflow = ticker.cashflow.T             # Cash flow statement (annual)
    balance_sheet = ticker.balance_sheet.T   # Balance sheet (annual)
    
    # Create helper to extract and structure
    def structure(series):
        data = []
        for date, value in series.items():
            if pd.notna(value):
                data.append({"end": str(date.date()), "val": int(value)})
        return data
    
    data = {
        "Revenue": structure(financials["Total Revenue"]),
        "OperatingCashFlow": structure(cashflow["Total Cash From Operating Activities"]),
        "CapitalExpenditures": structure(cashflow["Capital Expenditures"]),
        "TotalDebt": structure(balance_sheet["Total Debt"]),
    }
    
    # Compute Free Cash Flow = Operating Cash Flow - CapEx
    fcf_data = []
    for ocf, capex in zip(data["OperatingCashFlow"], data["CapitalExpenditures"]):
        if ocf["end"] == capex["end"]:
            fcf_data.append({
                "end": ocf["end"],
                "val": ocf["val"] + capex["val"]  # CapEx is usually negative in Yahoo data
            })
    data["FreeCashFlow"] = fcf_data

    # Return only latest values if requested
    if latest:
        latest_data = {}
        for key, values in data.items():
            latest_data[key] = values[0] if values else None
        return latest_data

    return data


# Example usage:
if __name__ == "__main__":
    symbol = "AAPL"
    print("Fetching historical data...")
    historical = fetch_apple_financials(symbol, latest=False)
    print(historical)

    print("\nFetching latest values...")
    latest = fetch_apple_financials(symbol, latest=True)
    print(latest)
