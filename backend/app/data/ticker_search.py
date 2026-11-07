import os
import requests
from dotenv import load_dotenv
from app.data.cache import get_cached, set_cache
from app.data.indian_markets import INDIA_NAME_TO_TICKER, is_indian_ticker

load_dotenv()
ALPHA_VANTAGE_KEY = os.getenv("ALPHA_VANTAGE_KEY")


def _local_india_search(query: str) -> list[dict]:
    """Fast local lookup for Indian company names — no API needed."""
    q = query.lower().strip()
    results = []
    seen = set()
    for name, symbol in INDIA_NAME_TO_TICKER.items():
        if q in name and symbol not in seen and not symbol.startswith("^"):
            seen.add(symbol)
            results.append({
                "symbol": symbol,
                "name": name.title(),
                "type": "Equity",
                "region": "India / NSE 🇮🇳",
            })
        if len(results) >= 5:
            break
    return results


def search_ticker(query: str) -> list[dict]:
    cache_key = f"ticker_search_{query.lower().replace(' ', '_')}"
    cached = get_cached(cache_key, max_age_seconds=604800)  # cache 7 days
    if cached is not None:
        return cached

    # 1. Try fast local Indian lookup first
    india_local = _local_india_search(query)

    # 2. Alpha Vantage global search
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "SYMBOL_SEARCH",
        "keywords": query,
        "apikey": ALPHA_VANTAGE_KEY,
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        matches = data.get("bestMatches", [])

        av_results = []
        for m in matches:
            symbol = m.get("1. symbol", "")
            region = m.get("4. region", "")
            # Tag Indian results clearly
            if is_indian_ticker(symbol) or "India" in region:
                region = region + " 🇮🇳" if "🇮🇳" not in region else region
            av_results.append({
                "symbol": symbol,
                "name": m.get("2. name"),
                "type": m.get("3. type"),
                "region": region,
            })

        # Merge: Indian local results first, then AV results (dedup by symbol)
        seen_symbols = {r["symbol"] for r in india_local}
        merged = india_local[:]
        for r in av_results:
            if r["symbol"] not in seen_symbols:
                merged.append(r)
                seen_symbols.add(r["symbol"])

        results = merged[:8]
        set_cache(cache_key, results)
        return results
    except Exception:
        # If AV fails, still return local Indian results
        return india_local