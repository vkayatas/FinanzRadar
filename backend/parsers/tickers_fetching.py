import os
import json
import requests
from collections import defaultdict

def download_and_unify_stocks(output_dir: str, file_nm:str, min_market_cap: float = 100_000_000):
    """
    Download NASDAQ, AMEX, and NYSE tickers, filter by market cap, 
    keep selected keys, remove duplicates, and save unified JSON.

    Args:
        output_dir (str): Directory to save the JSON file.
        min_market_cap (float): Minimum market cap to include.
    """
    # URLs for the three exchanges
    urls = [
        "https://raw.githubusercontent.com/rreichel3/US-Stock-Symbols/master/nasdaq/nasdaq_full_tickers.json",
        "https://raw.githubusercontent.com/rreichel3/US-Stock-Symbols/master/amex/amex_full_tickers.json",
        "https://raw.githubusercontent.com/rreichel3/US-Stock-Symbols/master/nyse/nyse_full_tickers.json",
    ]

    # Keys to keep
    keys_to_keep = ["symbol", "name", "industry", "country", "ipoyear", "marketCap"]

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
                # Keep selected keys, but convert marketCap to float
                new_stock_entry = {k: stock.get(k, "") for k in keys_to_keep}
                new_stock_entry["marketCap"] = int(market_cap) 
                
                # Use industry as sector tag 
                if 'industry' in stock:
                    new_stock_entry['sector'] = new_stock_entry.pop('industry') 
                    
                all_stocks[symbol] = new_stock_entry

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, file_nm)

    # Save unified JSON
    with open(output_file, "w") as f:
        json.dump(all_stocks, f, indent=2)

    print(f"Unified JSON saved with {len(all_stocks)} stocks at {output_file}")
    return all_stocks  # return the list if needed for further use

def build_prefix_map(unified_stocks, max_prefix_length: int, output_dir: str, file_nm: str):
    """
    Build a prefix map mapping prefixes to sets of symbols only.
    """
    prefix_map = defaultdict(set)  # prefix -> set of symbols

    for stock in unified_stocks.values():  # unified_stocks is dict from download_and_unify_stocks
        symbol = stock["symbol"].upper()
        name = stock["name"].lower()

        # Add symbol to all relevant prefixes (from symbol)
        symbol_lower = symbol.lower()
        for length in range(1, max_prefix_length + 1):
            prefix_map[symbol_lower[:length]].add(symbol)

        # Add symbol to all relevant prefixes (from name)
        for length in range(1, max_prefix_length + 1):
            prefix_map[name[:length]].add(symbol)

    # Convert sets to lists for JSON
    prefix_map_json = {k: list(v) for k, v in prefix_map.items()}

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Save prefix map
    with open(os.path.join(output_dir, file_nm), "w") as f:
        json.dump(prefix_map_json, f, indent=2)

    print(f"Prefix map saved with {len(prefix_map_json)} keys at {output_dir}/{file_nm}")

    return prefix_map_json