from app.scoring.sentiment import _finbert


def headline_attribution(headlines, top_n=8):
    """Return the headlines that moved sentiment the most, with FinBERT label and confidence."""
    if not headlines:
        return []

    results = _finbert(headlines, truncation=True)

    items = []
    for text, r in zip(headlines, results):
        label = r["label"]
        confidence = float(r["score"])
        if label == "positive":
            impact = confidence
        elif label == "negative":
            impact = -confidence
        else:
            impact = 0.0
        items.append({
            "headline": text,
            "label": label,
            "confidence": round(confidence, 3),
            "impact": round(impact, 3),
        })

    items.sort(key=lambda x: abs(x["impact"]), reverse=True)
    return items[:top_n]