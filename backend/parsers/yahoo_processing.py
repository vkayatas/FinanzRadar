import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime, timezone

from utils.math_utils import safe_dt
from utils.date_utils import safe_strftime
from utils.config.logging import init_logger
from utils.pandas_utils import safe_scalar, safe_dt

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

    def _dates_to_quarters(self, dates: pd.Series, quarterly:bool) -> pd.Series:
        dates = pd.to_datetime(dates)

        if not quarterly:
            return dates.dt.year.map(lambda y: f"CY{y}")
            # # Annual reports: map to nearest year-end
            # def nearest_year(dt):
            #     dec31 = pd.Timestamp(year=dt.year, month=12, day=31)
            #     # if date is closer to previous year's Dec 31, subtract 1
            #     return f"CY{dt.year - 1}" if (dt - dec31).days < -183 else f"CY{dt.year}"

            # return dates.apply(nearest_year)
        
        else:
            # Quarterly reports: map to nearest canonical quarter end
            def nearest_quarter(dt):
                year = dt.year
                quarters = {
                    pd.Timestamp(f"{year}-03-31"): f"CY{year}Q1",
                    pd.Timestamp(f"{year}-06-30"): f"CY{year}Q2",
                    pd.Timestamp(f"{year}-09-30"): f"CY{year}Q3",
                    pd.Timestamp(f"{year}-12-31"): f"CY{year}Q4",
                }
                nearest = min(quarters.keys(), key=lambda x: abs(x - dt))
                return quarters[nearest]
            
            return dates.apply(nearest_quarter)

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
        df["frame"] = self._dates_to_quarters(df["end"], quarterly=quarterly)
        
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
        current_price = hist['Close'].iloc[-1]
        prev_close = hist['Close'].iloc[-2]
        abs_change = round(current_price - prev_close, 2)
        rel_change = round((abs_change / prev_close) * 100, 2)

        # Helper to compute change over period
        def perf(period):
            today = hist.index[-1]

            if period == "1M":
                target_date = today - pd.DateOffset(months=1)
            elif period == "YTD":
                start = datetime(today.year, 1, 1, tzinfo=timezone.utc)
                # pick first available price on/after Jan 1
                ytd_data = hist.loc[hist.index >= start]
                if ytd_data.empty:
                    return None
                price_then = ytd_data['Close'].iloc[0]
                return {
                    "relStockPriceChange": round((current_price - price_then) / price_then * 100, 2),
                    "absStockPriceChange": round(current_price - price_then, 2),
                }
            elif period == "1Y":
                target_date = today - pd.DateOffset(years=1)
            elif period == "3Y":
                target_date = today - pd.DateOffset(years=3)
            elif period == "5Y":
                target_date = today - pd.DateOffset(years=5)
            else:
                return None

            # Find closest trading day on or before target_date
            past_data = hist.loc[hist.index <= target_date]
            if past_data.empty:
                return None
            past_price = past_data['Close'].iloc[-1]

            return {
                "relStockPriceChange": round((current_price - past_price) / past_price * 100, 2),
                "absStockPriceChange": round(current_price - past_price, 2),
            }

        # Fetch stock performance delta values
        perf_1M = perf("1M")
        perf_YTD = perf("YTD")
        perf_1Y = perf("1Y")
        perf_3Y = perf("3Y")
        perf_5Y = perf("5Y")

        # Build data struct
        data = {
            "currentPrice": round(current_price, 2),
            "relChange": rel_change,
            "absChange": abs_change,
            "lastUpdated": datetime.now(timezone.utc).isoformat(),
            
            # Unpack performance dicts into separate keys
            "performance_1M_rel": perf_1M.get("relStockPriceChange", None),
            "performance_1M_abs": perf_1M.get("absStockPriceChange", None),
            
            "performance_YTD_rel": perf_YTD.get("relStockPriceChange", None),
            "performance_YTD_abs": perf_YTD.get("absStockPriceChange", None),
            
            "performance_1Y_rel": perf_1Y.get("relStockPriceChange", None),
            "performance_1Y_abs": perf_1Y.get("absStockPriceChange", None),
            
            "performance_3Y_rel": perf_3Y.get("relStockPriceChange", None),
            "performance_3Y_abs": perf_3Y.get("absStockPriceChange", None),
            
            "performance_5Y_rel": perf_5Y.get("relStockPriceChange", None),
            "performance_5Y_abs": perf_5Y.get("absStockPriceChange", None),
            
            "ticker": symbol,
            "industry": info.get("industry", "N/A"),
            "sector": info.get("sector", "N/A"),
            "country": info.get("country", "N/A"),
        }

        return pd.DataFrame([data])

    def build_stock_kpi_dataframe(self, symbol: str):
        ticker = yf.Ticker(symbol)
        info = ticker.info
        financials = ticker.financials
        balance_sheet = ticker.balance_sheet
        
        def safe_get(key):
            val = info.get(key)
            return None if val is None or (isinstance(val, float) and pd.isna(val)) else val

        def ratio(a, b):
            return round(a / b, 2) if a and b and b != 0 else None

        # === VALUATION ===
        market_cap = safe_get("marketCap")
        trailing_pe = safe_get("trailingPE")
        forward_pe = safe_get("forwardPE")
        pb = safe_get("priceToBook")
        ps = safe_get("priceToSalesTrailing12Months")
        ev_ebitda = safe_get("enterpriseToEbitda")

        # === CASH FLOW ===
        total_cash = safe_get("totalCash")
        total_debt = safe_get("totalDebt")
        free_cashflow = safe_get("freeCashflow")

        # === MARGINS ===
        gross_margin = safe_get("grossMargins")
        op_margin = safe_get("operatingMargins")
        net_margin = safe_get("profitMargins")

        # Convert to percentages
        gross_margin = gross_margin * 100 if gross_margin is not None else None
        op_margin = op_margin * 100 if op_margin is not None else None
        net_margin = net_margin * 100 if net_margin is not None else None

        # === GROWTH ===
        revenue_growth = safe_get("revenueGrowth")
        earnings_growth = safe_get("earningsGrowth")
        
        # ROCE = EBIT / (Total Assets - Current Liabilities) * 100
        ebit = financials.loc['EBIT'].iloc[0]         
        total_assets = balance_sheet.loc['Total Assets'].iloc[0]
        current_liabilities = balance_sheet.loc['Current Liabilities'].iloc[0]

        roce = (ebit / (total_assets - current_liabilities)) * 100

        # ROIC = NOPAT / (Total Debt + Total Equity) * 100, with NOPAT ≈ EBIT*(1-tax_rate)
        tax_rate = 0.21  # approximate if info not available
        nopat = ebit * (1 - tax_rate)
        total_debt = safe_get("totalDebt")
        total_equity = balance_sheet.loc["Stockholders Equity"].iloc[0]

        roic = (nopat / (total_debt + total_equity)) * 100

        # Convert to percentages
        revenue_growth = revenue_growth * 100 if revenue_growth is not None else None
        earnings_growth = earnings_growth * 100 if earnings_growth is not None else None

        # === DIVIDENDS & EARNINGS ===
        trailing_eps = safe_get("trailingEps")
        forward_eps = safe_get("forwardEps")
        dividend_yield = safe_get("dividendYield")
        payout_ratio = safe_get("payoutRatio")

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
            "pe_trailing": round(trailing_pe, 2),
            "pe_forward": round(forward_pe, 2),
            "pb": round(pb, 2),
            "ps": round(ps, 2),
            "ev_ebitda": round(ev_ebitda, 2),
            
            # Cash Flow
            "totalCash": total_cash,
            "totalDebt": total_debt,
            "cashDebtRatio": cash_debt_ratio,
            "freeCashflow": free_cashflow,
            "debtToFCF": debt_to_fcf,
            
            # Margins
            "grossMargin": round(gross_margin, 2),
            "operatingMargin": round(op_margin, 2),
            "netMargin": round(net_margin, 2),
            
            # Growth
            "revenueGrowth": round(revenue_growth, 2),
            "earningsGrowth": round(earnings_growth, 2),
            "roce": round(roce, 2),
            "roic": round(roic, 2),
            
            # Dividend & Earnings
            "trailingEPS": trailing_eps,
            "forwardEPS": forward_eps,
            "dividendYield": dividend_yield,
            "payoutRatio": round(payout_ratio, 2),
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
