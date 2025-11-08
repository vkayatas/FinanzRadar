import os
import uvicorn
import pandas as pd
from functools import lru_cache
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from utils.data_viz_preprocessing import build_fundamental_data

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

@app.get("/stockInfo/{ticker}")
async def get_stock_info(ticker: str):
    ticker = ticker.upper().strip()
    url_logo = f"{LOGO_BASE_URL}/{ticker}.png"

    return {"logo_url": url_logo}

@app.get("/fundamentals_history/{ticker}")
async def get_fundamentals_history(ticker: str, form: str="10-K"):
    """
    Returns fundamental data for a given ticker and filing type.
    Example: GET /fundamentals/AAPL?form=10-K
    """
    ticker = ticker.upper().strip()
    path = os.path.join(FEATURESTORE_PATH, f"form={form}", f"ticker={ticker}")

    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail=f"No data found for {ticker} ({form}).")

    try:
        df = pd.read_parquet(path)
        result = build_fundamental_data(df, ticker, form)
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 
