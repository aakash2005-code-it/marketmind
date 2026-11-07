from transformers import pipeline

# Loaded once when the module is imported (not on every call) — model stays in memory
_finbert = pipeline("sentiment-analysis", model="ProsusAI/finbert")


def sentiment_score(headlines: list[str]) -> dict:
    if not headlines:
        return {
            "score": 0,
            "normalized": 0,
            "reasons": ["No recent news found"],
        }

    results = _finbert(headlines)

    positive = sum(1 for r in results if r["label"] == "positive")
    negative = sum(1 for r in results if r["label"] == "negative")
    neutral = sum(1 for r in results if r["label"] == "neutral")

    total = len(results)
    normalized = round((positive - negative) / total, 2)

    reasons = [
        f"{positive} positive, {negative} negative, {neutral} neutral headlines out of {total} analyzed (past 7 days)"
    ]

    return {
        "score": positive - negative,
        "normalized": normalized,
        "reasons": reasons,
    }