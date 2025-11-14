import time
import requests
import pandas as pd 
from typing import Optional
from functools import lru_cache

from utils.config.logging import init_logger
from utils.config.config import CACHE_SIZE, HEADERS

logger = init_logger(name=__name__, level="INFO", log_file="logs/app.log")

def safe_request(url: str, retries: int = 3, backoff: float = 0.5) -> Optional[dict]:
    for attempt in range(retries):
        try:
            r = requests.get(url, headers=HEADERS, timeout=10)
            if r.status_code == 200:
                return r.json()
        except requests.exceptions.RequestException as e:
            logger.warning(f"Request failed ({attempt+1}/{retries}): {e}")

        time.sleep(backoff * (2 ** attempt))  # exponential backoff
    return None

@lru_cache(maxsize=CACHE_SIZE)
def get_all_us_gaap_data(cik: str) -> Optional[dict]:
    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
    return safe_request(url)

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

@lru_cache(maxsize=32)
def build_fiscal_metadata(ticker: str, filing_types: tuple = ("10-K", "10-Q")) -> pd.DataFrame:    
    # Step 1: Get CIK and SEC data
    cik = get_cik_from_ticker(ticker)
    data = get_sec_submissions(cik)
    try:
        forms = data['filings']['recent']['form']
        report_dates = data['filings']['recent']['reportDate']
        filing_dates = data['filings']['recent']['filingDate']
        accession_numbers = data['filings']['recent']['accessionNumber']
    except KeyError:
        logger.warning(f"No SEC data for ticker='{ticker}'. Skip data fetching...")
        return(pd.DataFrame())

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