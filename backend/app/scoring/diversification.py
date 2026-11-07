import yfinance as yf
import pandas as pd

# Fixed basket spanning multiple sectors, so recommendations are diversified by construction
DEFAULT_BASKET = {
    "AAPL": "Technology", "MSFT": "Technology", "NVDA": "Technology",
    "JPM": "Financial Services", "V": "Financial Services",
    "JNJ": "Healthcare", "PFE": "Healthcare",
    "WMT": "Consumer Defensive", "KO": "Consumer Defensive",
    "XOM": "Energy",
    "HD": "Consumer Cyclical", "DIS": "Communication Services",
    "PG": "Consumer Defensive", "BAC": "Financial Services",
}


def _compute_metrics(ticker: str, period: str = "1y") -> dict | None:
    try:
        df = yf.Ticker(ticker).history(period=period)
        if df.empty or len(df) < 50:
            return None

        returns = df["Close"].pct_change().dropna()
        total_return = (df["Close"].iloc[-1] / df["Close"].iloc[0] - 1) * 100
        volatility = returns.std() * (252 ** 0.5) * 100  # annualized volatility %

        # simple risk-adjusted score: reward return, penalize volatility
        risk_adjusted_score = total_return / volatility if volatility > 0 else 0

        return {
            "ticker": ticker,
            "total_return_pct": round(total_return, 2),
            "volatility_pct": round(volatility, 2),
            "risk_adjusted_score": round(risk_adjusted_score, 3),
        }
    except Exception:
        return None


def build_diversified_recommendations(user_tickers: list[str] = None, top_n_sectors: int = 5) -> dict:
    basket = dict(DEFAULT_BASKET)

    # Merge in user's own search history tickers (sector unknown, label generically)
    if user_tickers:
        for t in user_tickers:
            t = t.upper()
            if t not in basket:
                basket[t] = "From your history"

    results = []
    for ticker, sector in basket.items():
        metrics = _compute_metrics(ticker)
        if metrics:
            metrics["sector"] = sector
            results.append(metrics)

    if not results:
        return {"recommendations": [], "note": "Could not compute recommendations right now."}

    df = pd.DataFrame(results)

    # Pick the single best risk-adjusted performer per sector -> real diversification
    best_per_sector = (
        df.sort_values("risk_adjusted_score", ascending=False)
        .groupby("sector", as_index=False)
        .first()
        .sort_values("risk_adjusted_score", ascending=False)
        .head(top_n_sectors)
    )

    recommendations = best_per_sector.to_dict(orient="records")

    return {
        "recommendations": recommendations,
        "note": "One top risk-adjusted performer per sector, selected from a diversified basket plus your search history.",
    }