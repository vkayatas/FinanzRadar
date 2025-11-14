
import shutil
import numpy as np
import pandas as pd

from utils.math_utils import safe_typecast
from utils.config.logging import init_logger

# Initialize logger
logger = init_logger(name=__name__, level="DEBUG", log_file="logs/app.log")

def safe_typecast_series(series, target_type="float"):
    return series.apply(lambda v: safe_typecast(v, target_type))

def safe_scalar(df, column):
    """Return the first non-null value in column or None."""
    if df is None or df.empty or column not in df.columns:
        return None
    val = df[column].dropna()
    return val.iloc[0] if not val.empty else None

def _convert_date_columns(df, columns: list, suffix: str="_dt"):
    for col in columns:
        if col in df.columns:
            df[col + suffix] = pd.to_datetime(df[col], errors='coerce')
    return df

def _round_columns(df, columns, decimals=2):
    for col in columns:
        if col in df.columns:
            df[col] = df[col].round(decimals)
    return df

def write_ticker_partitioned_parquet(df: pd.DataFrame, output_dir: str, partition_cols: list, ticker:str, form:str, overwrite=True, engine: str = 'pyarrow'):
    ticker_dir = output_dir.joinpath(*[f"{col}={val}" for col, val in {"ticker": ticker, "form": form}.items() if val and col in partition_cols])
    
    if not df.empty:
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Delete entire parent directory if it exists
        if (ticker_dir.exists()) and (overwrite):
            shutil.rmtree(ticker_dir)

        # Write DataFrame partitioned by the columns
        df.to_parquet(output_dir, partition_cols=partition_cols, engine=engine, index=False)