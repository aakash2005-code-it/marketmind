THRESHOLDS = {"technical": 0.05, "fundamental": 0.5, "sentiment": 0.10}

PHRASE = {
    "technical": "the technical signal",
    "fundamental": "the fundamental signal",
    "sentiment": "the sentiment signal",
}


def _label(key, score):
    t = THRESHOLDS[key]
    if score >= t:
        return "bullish"
    if score <= -t:
        return "bearish"
    return "neutral"


def _join(items):
    if len(items) == 1:
        return items[0]
    return ", ".join(items[:-1]) + " and " + items[-1]


def _verb(n):
    return "leans" if n == 1 else "lean"


def detect_signal_conflict(breakdown):
    scores = {k: float(breakdown[k]) for k in THRESHOLDS}
    labels = {k: _label(k, v) for k, v in scores.items()}

    up = [k for k, v in labels.items() if v == "bullish"]
    down = [k for k, v in labels.items() if v == "bearish"]
    flat = [k for k, v in labels.items() if v == "neutral"]

    if up and down:
        status = "conflict"
        message = (
            f"Signals disagree: {_join([PHRASE[k] for k in up])} {_verb(len(up))} positive, "
            f"while {_join([PHRASE[k] for k in down])} {_verb(len(down))} negative. "
            "Treat this verdict with extra caution and check how it changes under your own weighting."
        )
    elif len(up) == 3 or len(down) == 3:
        status = "agree"
        direction = "positive" if up else "negative"
        message = f"All three signals lean {direction}, so the verdict does not rest on a single signal."
    elif not up and not down:
        status = "weak"
        message = "All three signals are close to neutral, so this verdict rests on weak evidence."
    else:
        status = "aligned"
        leaning = up or down
        direction = "positive" if up else "negative"
        message = (
            f"No signal opposes the others. {_join([PHRASE[k] for k in leaning])} "
            f"{_verb(len(leaning))} {direction}; {_join([PHRASE[k] for k in flat])} "
            f"{'is' if len(flat) == 1 else 'are'} neutral."
        )

    return {
        "status": status,
        "labels": labels,
        "scores": {k: round(v, 3) for k, v in scores.items()},
        "message": message,
        "thresholds": THRESHOLDS,
    }