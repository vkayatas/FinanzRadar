from parsers.tickers_fetching import download_and_unify_stocks, build_prefix_map

min_market_cap = 2_000_000_000
ticker_search_output_dir = "vue-frontend/src/assets"

unified_stocks = download_and_unify_stocks(output_dir=ticker_search_output_dir, min_market_cap=min_market_cap, file_nm="_tickerSearchUS.json")
build_prefix_map(unified_stocks, max_prefix_length=3, output_dir=ticker_search_output_dir, file_nm="_tickerSearchUSMap.json")