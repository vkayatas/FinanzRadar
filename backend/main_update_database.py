import os
import time
import json
import pandas as pd
from tqdm import tqdm
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed, ThreadPoolExecutor

from parsers.sec import SecProcessing
from parsers.yahoo_processing import YahooProcessing 
from utils.config.logging import init_logger
from utils.pandas_utils import write_ticker_partitioned_parquet

# Initialize logger
logger = init_logger(name=__name__, level="DEBUG", log_file="logs/app.log")

def fetch_ticker(key:str, ticker, fetch_fn, output_dir, overwrite, filing_type, partition_cols):
    start_time = time.time()
    ticker_dir = output_dir.joinpath(*[f"{col}={val}" for col, val in {"ticker": ticker, "form": filing_type}.items() if val and col in partition_cols])
    parquet_files = list(ticker_dir.glob("*.parquet"))

    # Skip if already exists and not overwriting
    if parquet_files and not overwrite and any(f.stat().st_size > 0 for f in parquet_files):
        logger.info(f"[SKIP] {ticker} already exists at {ticker_dir}")
        return None

    # Call fetch_fn dynamically
    try:
        result = fetch_fn(ticker, filing_type=filing_type) if filing_type else fetch_fn(ticker)
    except Exception as e:
        logger.error(f"{ticker} fetch failed: {e}")
        return None
        
    if result is not None:
        elapsed = time.time() - start_time
        logger.info(f"Fetching function '{key}' took {elapsed:.2f} seconds.")

        try:
            if key == "earnings":
                for earnings_label, df in result.items():
                    write_ticker_partitioned_parquet(df, form=filing_type, ticker=ticker, partition_cols=partition_cols, output_dir=output_dir / earnings_label)
                    
            elif isinstance(result, pd.DataFrame):
                write_ticker_partitioned_parquet(result, form=filing_type, ticker=ticker, partition_cols=partition_cols, output_dir=output_dir)
            else:
                logger.error(f"Upsi, shouldnt happen. Like we should programatically never reach this.")
                raise KeyError("Upsi")
        except Exception as e:
            logger.error(f"Writing parquet for {ticker} failed: {e}")
    else:
        logger.warning(f"[EMPTY] No data for {ticker}")

    return None

def fetch_all(key, tickers, fetch_fn, output_dir, partition_cols, max_workers=1, executor="process", overwrite=False, filing_type=None):
    output_dir.mkdir(parents=True, exist_ok=True)
    Executor = ThreadPoolExecutor if executor == "thread" else ProcessPoolExecutor
    
    # Log selected settings
    logger.debug(f"Executor type: {Executor.__name__}, max_workers: {max_workers}, output_dir: {output_dir}")
    
    with Executor(max_workers=max_workers) as executor:
        future_to_ticker = {
            executor.submit(fetch_ticker, key, ticker, fetch_fn, output_dir, overwrite, filing_type, partition_cols): ticker
            for ticker in tickers
        }

        for future in tqdm(as_completed(future_to_ticker), total=len(future_to_ticker), desc=f"Fetching {output_dir.name}"):
            ticker = future_to_ticker[future]
            try:
                future.result()
                #tqdm.write(f"✅ Done: {ticker}")
            except Exception as e:
                tqdm.write(f"❌ Error: {ticker} — {e}")

    logger.info(f"✅ Finished fetching {len(tickers)} tickers for {output_dir.name}")
        
def _init_data_source_config(config_path:str):
    data_sources = []
    sec = SecProcessing()
    yp = YahooProcessing()
    
    # Step 1: Load config
    config_path = Path(config_path)
    with open(config_path) as f:
        config = json.load(f)
    tickers = config.get("tickers", [])

    # Step 2: Map config keys to fetch functions
    FETCH_FN_MAP = {
        "fundamentals": sec.get_company_metrics_history,
        "info": yp._ticker_info,
        "kpis": yp.build_stock_kpi_dataframe,
        "earnings": yp.get_earnings_data
    }
    
    # Step 3: Build data source config
    for key, cfg in config.items():
        valid_data_sources = ["fundamentals", "info", "kpis", "earnings"]
        if key not in valid_data_sources:
            logger.info(f"Skipped key='{key}' since its not in data_sources: {valid_data_sources} ")
            continue

        output_dir = Path(cfg["output_dir"])
        partition_cols = cfg.get("partition_cols", ["ticker"])
        overwrite = cfg.get("OVERWRITE", False)
        filing_type = cfg.get("mode") if key == "fundamentals" else None
        max_workers = cfg.get("max_workers") if cfg.get("max_workers") is not None else 16
        max_workers = min(max_workers, os.cpu_count())  
        
        data_sources.append({
            "key": key,
            "output_dir": output_dir,
            "fetch_fn": FETCH_FN_MAP[key],
            "partition_cols": partition_cols,
            "overwrite": overwrite,
            "filing_type": filing_type,
            "tickers": tickers,
            "executor": cfg.get("executor", "process"),
            "max_workers": max_workers
        })
    
    return data_sources

if __name__ == "__main__":
    config_path = "finanzradar/utils/config/financial_data_config.json"
                
    # Build data_sources dynamically from config
    data_sources = _init_data_source_config(config_path)

    # Fetch & write all data
    for source in data_sources:
        start_time = time.time()
        fetch_all(tickers=source["tickers"], fetch_fn=source["fetch_fn"], output_dir=source["output_dir"], max_workers=source["max_workers"], executor=source["executor"], overwrite=source["overwrite"], filing_type=source["filing_type"], partition_cols=source["partition_cols"], key=source["key"])
        
    logger.info(f"Total time: {time.time() - start_time:.2f}s")