import yfinance as yf
import pandas as pd
from app.data.cache import get_cached, set_cache

def get_price_history(ticker: str, period: str = "6mo") -> pd.DataFrame:
    cache_key = f"prices_{ticker}_{period}"
    cached = get_cached(cache_key, max_age_seconds=3600)  # 1 hour

    if cached is not None:
        df = pd.DataFrame(cached)
        df["Date"] = pd.to_datetime(df["Date"], utc=True)
        df.set_index("Date", inplace=True)
        return df

    stock = yf.Ticker(ticker)
    df = stock.history(period=period)

    if df is not None and not df.empty:
        df = df.dropna(subset=["Close"])

    if df is None or df.empty:
        raise ValueError(f"No price data found for ticker: {ticker}")

    to_cache = df.reset_index()
    to_cache["Date"] = to_cache["Date"].astype(str)
    set_cache(cache_key, to_cache.to_dict(orient="records"))

    return df