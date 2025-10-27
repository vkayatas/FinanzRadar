import os
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from functools import lru_cache

# Config
DEFAULT_ALLOWED_ORIGINS = "http://localhost:3000"
LOGO_BASE_URL = "https://storage.googleapis.com/iex/api/logos"

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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)  # production-safe binding
