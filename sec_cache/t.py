import requests
import json

# URLs for the three exchanges
urls = [
    "https://raw.githubusercontent.com/rreichel3/US-Stock-Symbols/master/nasdaq/nasdaq_full_tickers.json",
    "https://raw.githubusercontent.com/rreichel3/US-Stock-Symbols/master/amex/amex_full_tickers.json",
    "https://raw.githubusercontent.com/rreichel3/US-Stock-Symbols/master/nyse/nyse_full_tickers.json",
]

# Keys to keep
keys_to_keep = ["symbol", "name", "sector", "country", "ipoyear", "marketCap"]

# Minimum market cap
min_market_cap = 100_000_000

# Dictionary to avoid duplicates by symbol
all_stocks = {}

for url in urls:
    print(f"Downloading: {url}")
    response = requests.get(url)
    response.raise_for_status()
    tickers = response.json()

    for stock in tickers:
        try:
            market_cap = float(stock.get("marketCap", 0))
        except (ValueError, TypeError):
            continue
        if market_cap < min_market_cap:
            continue
        
        symbol = stock.get("symbol")
        if symbol not in all_stocks:
            all_stocks[symbol] = {k: stock.get(k, "") for k in keys_to_keep}

# Convert dictionary to list
unified_list = list(all_stocks.values())

# Save unified JSON
with open("us_stocks_unified.json", "w") as f:
    json.dump(unified_list, f, indent=2)

print(f"Unified JSON saved with {len(unified_list)} stocks")
