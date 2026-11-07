from app.data.technical_data import get_price_history
from app.data.fundamentals_data import get_fundamentals
from app.data.news_data import get_recent_headlines
from app.scoring.technical_ml import technical_score_ml
from app.scoring.fundamentals import fundamentals_score
from app.scoring.sentiment import sentiment_score
from app.ensemble.combiner import combine_scores


def quick_verdict(resolved_ticker: str) -> dict:
    df = get_price_history(resolved_ticker)
    if df is not None and not df.empty:
        df = df.dropna(subset=["Close"])

    fundamentals = get_fundamentals(resolved_ticker)
    headlines = get_recent_headlines(resolved_ticker, None)

    tech = technical_score_ml(df)
    fund = fundamentals_score(fundamentals)
    sent = sentiment_score(headlines)
    result = combine_scores(tech, fund, sent)

    closes = df["Close"].dropna() if df is not None and not df.empty else []
    price = float(closes.iloc[-1]) if len(closes) > 0 else 0.0

    return {
        "verdict": result["verdict"],
        "investment_score": float(result["investment_score"]),
        "latest_price": round(price, 2),
    }