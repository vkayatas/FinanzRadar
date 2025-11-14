import os
import uvicorn
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from utils.data_viz_preprocessing import get_earnings_columns, build_fundamental_data, build_stock_info_data, build_stock_kpi_groups, build_historical_earnings_data, build_next_earnings_data, build_eps_scatter_series

PORT = 8000
HOST = "0.0.0.0"

# Config
DEFAULT_ALLOWED_ORIGINS = ["http://localhost:5173"]
LOGO_BASE_URL = "https://storage.googleapis.com/iex/api/logos"
FEATURESTORE_PATH = "backend/featurestore/20_silver"

# Init app
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=DEFAULT_ALLOWED_ORIGINS,  # can configure multiple origins via env
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# @app.get("/stockLogoUrl/{ticker}")
# async def get_stock_logo_url(ticker: str):
#     ticker = ticker.upper().strip()
#     url_logo = f"{LOGO_BASE_URL}/{ticker}.png"

#     return {"logo_url": url_logo}

@app.get("/fundamentals_history/{ticker}")
async def get_fundamentals_history(ticker: str, form: str="10-K"):
    """
    Returns fundamental data for a given ticker and filing type.
    Example: GET /fundamentals/AAPL?form=10-K
    """
    ticker = ticker.upper().strip()
    path = os.path.join(FEATURESTORE_PATH, "fundamentals", f"ticker={ticker}", f"form={form}")

    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail=f"No data found for {ticker} ({form}).")

    try:
        df = pd.read_parquet(path)
        result = build_fundamental_data(df, ticker, form)
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stock_info/{ticker}")
async def get_stock_info_data(ticker: str):
    """
    Returns fundamental data for a given ticker and filing type.
    Example: GET /stock_info/AAPL
    """
    ticker = ticker.upper().strip()
    path = os.path.join(FEATURESTORE_PATH, "info", f"ticker={ticker}")

    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail=f"No stock info data found for {ticker}.")

    try:
        df = pd.read_parquet(path)
        result = build_stock_info_data(df)
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/kpis/{ticker}")
async def get_stock_kpi_data(ticker: str):
    """
    Returns fundamental data for a given ticker and filing type.
    Example: GET /kpis/AAPL
    """
    ticker = ticker.upper().strip()
    path = os.path.join(FEATURESTORE_PATH, "kpis", f"ticker={ticker}")

    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail=f"No stock info data found for {ticker}.")

    try:
        df = pd.read_parquet(path)
        result = build_stock_kpi_groups(df)
        
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/earnings/{ticker}")
async def get_earnings_data(ticker: str):
    """
    Returns fundamental data for a given ticker and filing type.
    Example: GET /kpis/AAPL
    """
    data = {
        "columns" : get_earnings_columns(),
        "calls" : {},
        "scatterSeries" : {},
        "nextEarnings" : {},
    }

    ticker = ticker.upper().strip()
    for elem, key, func in zip(["historical", "historical", "next"], ["calls", "scatterSeries", "nextEarnings"], [build_historical_earnings_data, build_eps_scatter_series, build_next_earnings_data]):
        path = os.path.join(FEATURESTORE_PATH, "earnings", elem, f"ticker={ticker}")

        if not os.path.exists(path):
            raise HTTPException(status_code=404, detail=f"No stock info data found for {ticker}.")

        try:
            df = pd.read_parquet(path)
            result = func(df)
            data[key] = result 
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
    return JSONResponse(content=data)
    
    
if __name__ == "__main__":
    uvicorn.run(app, host=HOST, port=PORT) 
