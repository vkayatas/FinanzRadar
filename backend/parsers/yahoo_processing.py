import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime, timezone

from utils.pandas_utils import safe_scalar, perf
from utils.config.logging import init_logger
from utils.date_utils import safe_dt, safe_strftime, _dates_to_quarters
from utils.math_utils import safe_get, ratio, safe_round

# Initialize logger
logger = init_logger(name=__name__, level="INFO", log_file="logs/app.log")

YFINANCE_METRICS = {
    # Balance Sheet
    "TotalCurrentAssets": ["Current Assets"],
    "TotalAssets": ["Total Assets"],
    "ShortTermDebt": ["Current Debt"],  # or Current Debt And Capital Lease Obligation
    "TotalCurrentLiabilities": ["Current Liabilities"],
    "LongTermDebt": ["Long Term Debt"],
    "TotalLiabilities": ["Total Liabilities Net Minority Interest"],  # best approximation
    "StockholdersEquity": ["Stockholders Equity"],
    
    # Operations / Income Statement
    "Revenue": ["Total Revenue"],
    "ResearchAndDevelopment": ["Research And Development"],
    "CostOfRevenue": ["Cost Of Revenue"],
    "GrossProfit": ["Gross Profit"],
    "TotalOperatingExpenses": ["Total Expenses"],
    "OperatingIncome": ["Operating Income"],
    "NonOperatingIncomeExpense": ["Other Non Operating Income Expenses"],
    "DepreciationAmortization": ["Depreciation And Amortization", "Depreciation Amortization Depletion"],
    "NetIncome": ["Net Income"],
    "BasicEps": ["Basic EPS"],
    "DilutedEps": ["Diluted EPS"],
    "SharesOutstandingBasic": ["Basic Average Shares"],
    "SharesOutstandingDiluted": ["Diluted Average Shares"],
    "SharesOutstanding": [],  # sometimes not directly available
    
    # Cashflow
    "StockBasedCompensation": ["Stock Based Compensation"],
    "OperatingCashFlow": ["Operating Cash Flow", "Cash Flow From Continuing Operating Activities"],
    "TotalCash": ["Cash And Cash Equivalents", "Cash Cash Equivalents And Short Term Investments"],
    "DividendsPaid": ["Cash Dividends Paid", "Common Stock Dividend Paid"],
    "StockBuybacks": ["Repurchase Of Capital Stock", "Common Stock Payments"],
    "CapitalExpenditures": ["Capital Expenditure", "Purchase Of PPE"],
    "InterestExpense": ["Interest Expense"],
    # Optional / advanced
    "FreeCashFlow": ["Free Cash Flow"],  # if you want to add
}

DEFAULT_TAX_RATE = 0.21

class YahooProcessing:
    def _align_previous_available_dates(self, dates: pd.DatetimeIndex, source_index: pd.DatetimeIndex):
        dates = pd.to_datetime(dates).values.astype("datetime64[ns]")
        source_index = np.sort(source_index.values.astype("datetime64[ns]"))
        
        # searchsorted finds insertion point
        idx = np.searchsorted(source_index, dates, side="right") - 1
        idx[idx < 0] = 0  # if no previous available, pick first element

        return pd.to_datetime(source_index[idx])

    def get_market_cap_exact_dates(self, ticker_symbol: str, dates: pd.DatetimeIndex) -> pd.Series:
        ticker = yf.Ticker(ticker_symbol)
        
        # Ensure datetime and normalize
        dates = pd.to_datetime(dates).normalize()
        start_date = dates.min() 
        end_date = dates.max()

        # Shares
        shares_outstanding = ticker.get_shares_full(start=start_date - pd.DateOffset(years=1))
        if shares_outstanding is None:
            return pd.Series()
        
        shares_outstanding.index = shares_outstanding.index.tz_localize(None)
        shares_outstanding = shares_outstanding[~shares_outstanding.index.duplicated()]

        # Prices
        prices = ticker.history(start=start_date - pd.DateOffset(days=45), end=end_date, interval="1d")["Close"]
        prices.index = prices.index.tz_localize(None)

        # Reindex + forward fill
        aligned_dates_prices = self._align_previous_available_dates(dates, prices.index)
        aligned_dates_shares = self._align_previous_available_dates(dates, shares_outstanding.index)
        shares_aligned = shares_outstanding.reindex(aligned_dates_shares).values
        prices_aligned = prices.reindex(aligned_dates_prices).values

        # Build final Series
        market_cap =  pd.Series(prices_aligned * shares_aligned, index=dates, name="MarketCap").astype("int")

        return market_cap

    def fetch_financials(self, symbol: str, quarterly: bool = False) -> pd.DataFrame:
        ticker = yf.Ticker(symbol)
        
        # Pick annual vs quarterly
        financials = ticker.quarterly_financials.T if quarterly else ticker.financials.T
        cashflow = ticker.quarterly_cashflow.T if quarterly else ticker.cashflow.T
        balance_sheet = ticker.quarterly_balance_sheet.T if quarterly else ticker.balance_sheet.T
        
        def structure(series):
            def safe_cast(v):
                return int(v) if float(v).is_integer() else float(v)
            return [
                {"end": str(date.date()), "val": safe_cast(value)}
                for date, value in series.items() if pd.notna(value)
            ]

        # Fetch data
        data = {}
        for key, possible_cols in YFINANCE_METRICS.items():
            for col in possible_cols:
                for stmt in (financials, cashflow, balance_sheet):
                    if col in stmt:
                        data[key] = structure(stmt[col])
                        break
                if key in data:
                    break
        
        # Convert to DataFrame
        df = pd.DataFrame({key: pd.Series({item["end"]: item["val"] for item in values}) 
                        for key, values in data.items()})
        df = df.sort_index(ascending=False)
        
        # Add metadata
        df["MarketCap"] = self.get_market_cap_exact_dates(symbol, df.index.tolist())
        df["end"] = df.index
        df["ticker"] = symbol
        df["form"] = "10-Q" if quarterly else "10-K"
        df["frame"] = _dates_to_quarters(df["end"], quarterly=quarterly)
        
        # Data cleaning
        for col in ["StockBuybacks", "CapitalExpenditures", "DividendsPaid"]:
            if col in df.columns:
                df[col] = df[col].abs()

        return df

    def _ticker_info(self, symbol: str):
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="6y", interval="1d")

        if hist.empty:
            raise ValueError(f"No historical data found for {symbol}")

        # Get current data
        info = ticker.info
        current_price = safe_get(hist, "Close", index=-1)
        prev_close = safe_get(hist, "Close", index=-2)
        abs_change = safe_round(current_price - prev_close, 2)
        rel_change = safe_round((abs_change / prev_close) * 100, 2)

        # Fetch stock performance delta values
        perf_1M = perf(hist, current_price, period="1M", prefix="StockPriceChange")
        perf_YTD = perf(hist, current_price, period="YTD", prefix="StockPriceChange")
        perf_1Y = perf(hist, current_price, period="1Y", prefix="StockPriceChange")
        perf_3Y = perf(hist, current_price, period="3Y", prefix="StockPriceChange")
        perf_5Y = perf(hist, current_price, period="5Y", prefix="StockPriceChange")

        # Build data struct
        data = {
            "currentPrice": safe_round(current_price, 2),
            "relChange": rel_change,
            "absChange": abs_change,
            "lastUpdated": datetime.now(timezone.utc).isoformat(),
            
            # Unpack performance dicts into separate keys
            "performance_1M_rel": safe_get(perf_1M, "relStockPriceChange"),
            "performance_1M_abs": safe_get(perf_1M, "absStockPriceChange"),
            
            "performance_YTD_rel": safe_get(perf_YTD, "relStockPriceChange"),
            "performance_YTD_abs": safe_get(perf_YTD, "absStockPriceChange"),
            
            "performance_1Y_rel": safe_get(perf_1Y, "relStockPriceChange"),
            "performance_1Y_abs": safe_get(perf_1Y, "absStockPriceChange"),
            
            "performance_3Y_rel": safe_get(perf_3Y, "relStockPriceChange"),
            "performance_3Y_abs": safe_get(perf_3Y, "absStockPriceChange"),
            
            "performance_5Y_rel": safe_get(perf_5Y, "relStockPriceChange"),
            "performance_5Y_abs": safe_get(perf_5Y, "absStockPriceChange"),
            
            "ticker": symbol,
            "industry": info.get("industry", "N/A"),
            "sector": info.get("sector", "N/A"),
            "country": info.get("country", "N/A"),
        }

        return pd.DataFrame([data])

    def build_stock_kpi_dataframe(self, symbol: str):
        ticker = yf.Ticker(symbol)
        info = ticker.info
        financials = ticker.financials.T
        balance_sheet = ticker.balance_sheet.T

        # === VALUATION ===
        market_cap = safe_get(info, "marketCap")
        trailing_pe = safe_get(info, "trailingPE")
        forward_pe = safe_get(info, "forwardPE")
        pb = safe_get(info, "priceToBook")
        ps = safe_get(info, "priceToSalesTrailing12Months")
        ev_ebitda = safe_get(info, "enterpriseToEbitda")

        # === CASH FLOW ===
        total_cash = safe_get(info, "totalCash")
        total_debt = safe_get(info, "totalDebt")
        free_cashflow = safe_get(info, "freeCashflow")

        # === MARGINS ===
        gross_margin = safe_get(info, "grossMargins")
        op_margin = safe_get(info, "operatingMargins")
        net_margin = safe_get(info, "profitMargins")

        # Convert to percentages
        gross_margin = gross_margin * 100 if gross_margin is not None else None
        op_margin = op_margin * 100 if op_margin is not None else None
        net_margin = net_margin * 100 if net_margin is not None else None

        # === GROWTH ===
        revenue_growth = safe_get(info, "revenueGrowth")
        earnings_growth = safe_get(info, "earningsGrowth")
        
        # ROCE = EBIT / (Total Assets - Current Liabilities) * 100
        ebit = safe_get(financials, "EBIT", index=0)         
        total_assets = safe_get(balance_sheet, "Total Assets", index=0)
        current_liabilities = safe_get(balance_sheet, "Current Liabilities", index=0) 

        if total_assets is None or current_liabilities is None or ebit is None:
            roce = None
        else:
            roce = (ebit / (total_assets - current_liabilities)) * 100

        # ROIC = NOPAT / (Total Debt + Total Equity) * 100, with NOPAT ≈ EBIT*(1-tax_rate)
        tax_rate = safe_get(financials, "Tax Rate For Calcs", index=0) if safe_get(financials, "Tax Rate For Calcs", index=0) is not None else DEFAULT_TAX_RATE # approximate if info not available
        nopat = ebit * (1 - tax_rate)
        total_debt = safe_get(info, "totalDebt")
        total_equity = safe_get(balance_sheet, "Stockholders Equity", index=0)

        if nopat is None or total_debt is None or total_equity is None:
            roic = None
        else:
            roic = (nopat / (total_debt + total_equity)) * 100

        # Convert to percentages
        revenue_growth = revenue_growth * 100 if revenue_growth is not None else None
        earnings_growth = earnings_growth * 100 if earnings_growth is not None else None

        # === DIVIDENDS & EARNINGS ===
        trailing_eps = safe_get(info, "trailingEps")
        forward_eps = safe_get(info, "forwardEps")
        dividend_yield = safe_get(info, "dividendYield")
        payout_ratio = safe_get(info, "payoutRatio")

        # === CALENDAR DATES ===
        earnings_date = None
        ex_div_date = None
        div_date = None
        calendar = ticker.calendar
        
        if calendar:
            earnings_date = safe_strftime(calendar.get("Earnings Date"))
            div_date = safe_strftime(calendar.get("Dividend Date"))
            ex_div_date = safe_strftime(calendar.get("Ex-Dividend Date"))
            
        # === DERIVED METRICS ===
        cash_debt_ratio = ratio(total_cash, total_debt)
        debt_to_fcf = ratio(total_debt, free_cashflow)

        # === BUILD A SINGLE ROW DICT ===
        data = {
            "ticker": symbol,
            "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            # Valuation
            "marketCap": market_cap,
            "pe_trailing": safe_round(trailing_pe, 2),
            "pe_forward": safe_round(forward_pe, 2),
            "pb": safe_round(pb, 2),
            "ps": safe_round(ps, 2),
            "ev_ebitda": safe_round(ev_ebitda, 2),
            
            # Cash Flow
            "totalCash": total_cash,
            "totalDebt": total_debt,
            "cashDebtRatio": cash_debt_ratio,
            "freeCashflow": free_cashflow,
            "debtToFCF": debt_to_fcf,
            
            # Margins
            "grossMargin": safe_round(gross_margin, 2),
            "operatingMargin": safe_round(op_margin, 2),
            "netMargin": safe_round(net_margin, 2),
            
            # Growth
            "revenueGrowth": safe_round(revenue_growth, 2),
            "earningsGrowth": safe_round(earnings_growth, 2),
            "roce": safe_round(roce, 2),
            "roic": safe_round(roic, 2),
            
            # Dividend & Earnings
            "trailingEPS": trailing_eps,
            "forwardEPS": forward_eps,
            "dividendYield": dividend_yield,
            "payoutRatio": safe_round(payout_ratio, 2),
            "nextEarningsDate": earnings_date,
            "exDividendDate": ex_div_date,
            "payoutDate": div_date,
        }

        df = pd.DataFrame([data])
        return df

    def get_earnings_data(self, symbol: str, window_days: int = 14):
        ticker = yf.Ticker(symbol)
        next_earnings = {}
        
        # === HISTORICAL EARNINGS ===
        ed = ticker.earnings_dates  # DataFrame (Yahoo may cap to ~8 quarters)
        if ed is None or ed.empty:
            return None

        df = ed.reset_index()
        df.rename(columns={
            'Earnings Date': 'date',
            'EPS Estimate': 'epsEstimate',
            'Reported EPS': 'epsReported',
        }, inplace=True)

        # Add delta percentage and metadata columns
        df["epsDelta"] = ((df["epsReported"] - df["epsEstimate"]) / df["epsEstimate"] * 100).round(2)
        df["date"] = pd.to_datetime(df["date"]).dt.tz_convert(None)
        df["ticker"] = symbol
        
        # Append sec_filing column to df
        filings = ticker.sec_filings
        if filings: # Dict not empty
            filings = pd.DataFrame(ticker.sec_filings)
            if filings is not None and not filings.empty:
                filings = filings[filings["type"].isin(["10-K", "10-Q"])].copy()
                filings["Filing Date"] = pd.to_datetime(filings["date"])
                filings.sort_values("Filing Date", inplace=True, ascending=False)
            else:
                filings = pd.DataFrame(columns=["Filing Date", "type", "edgarUrl"])

            # === Match all filings within a time window around each earnings date ===
            sec_links = []
            for date in df["date"]:
                mask = (
                    (filings["Filing Date"] >= date - pd.Timedelta(days=window_days)) &
                    (filings["Filing Date"] <= date + pd.Timedelta(days=window_days))
                )
                matched = filings.loc[mask, "edgarUrl"].tolist()
                sec_links.append(", ".join(matched) if matched else None)

            df["sec_filing"] = sec_links
            
            # === NEXT EARNINGS EVENT ===
            latest_10k = filings[filings["type"] == "10-K"].dropna(how="all").head(1)
            latest_10q = filings[filings["type"] == "10-Q"].dropna(how="all").head(1)
            
            # Append to dict
            next_earnings.update({
                "latest10kUrl": safe_scalar(latest_10k, "edgarUrl"),
                "latest10kDate": safe_scalar(latest_10k, "date").strftime("%Y-%m-%d") if safe_scalar(latest_10k, "date") else None,
                "latest10qUrl": safe_scalar(latest_10q, "edgarUrl"), 
                "latest10qDate": safe_scalar(latest_10q, "date").strftime("%Y-%m-%d") if safe_scalar(latest_10q, "date") else None
            })
            
        cal = ticker.calendar or {}
        if cal:
            next_earnings_dt = safe_dt(cal.get("Earnings Date"))
            dividend_ex_date = safe_dt(cal.get("Ex-Dividend Date"))

            next_earnings.update({
                "nextEarningsDate": next_earnings_dt,
                "epsEstimate": ed["EPS Estimate"].iloc[0] if "EPS Estimate" in ed.columns else None,
                "dividendExDate": dividend_ex_date,
                "expectedDividend": ticker.info.get("dividendRate", None),
            })
        
        # To Dataframe
        df_next = pd.DataFrame([next_earnings])
        df_next["ticker"] = symbol

        return {
            "historical": df,
            "next": df_next
        }

# Example usage:
if __name__ == "__main__":
    symbol = "AAPL"
    logger.info("Fetching stock info, kpis & earnings...")
    yp = YahooProcessing()
    info = yp._ticker_info(symbol)
    kpis = yp.build_stock_kpi_dataframe(symbol)
    earnings = yp.get_earnings_data(symbol)
    
    logger.info("Fetching historical data...")
    #historical_annual = fetch_financials(symbol, quarterly=False)
    #historical_quarterly = fetch_financials(symbol, quarterly=True)
    #print(historical_annual)
