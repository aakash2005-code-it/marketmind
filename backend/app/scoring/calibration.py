import numpy as np
import pandas as pd
import xgboost as xgb

from app.data.cache import get_cached, set_cache
from app.scoring.technical_ml import FEATURES
from app.scoring.track_record import BASKET, TRAIN_FRACTION, PURGE_DAYS, _load_ticker_frame

BIN_EDGES = [0.0, 0.45, 0.50, 0.55, 0.60, 1.01]
MIN_BIN_COUNT = 30
CACHE_KEY = "calibration_v1"


def _label(lo, hi):
    if lo <= 0.0:
        return f"below {int(hi * 100)}%"
    if hi > 1.0:
        return f"{int(lo * 100)}% and above"
    return f"{int(lo * 100)}-{int(hi * 100)}%"


def run_calibration(force: bool = False) -> dict:
    if not force:
        cached = get_cached(CACHE_KEY, max_age_seconds=7 * 86400)
        if cached is not None:
            return cached

    frames = {}
    for ticker in BASKET:
        try:
            frame = _load_ticker_frame(ticker)
            if frame is not None:
                frames[ticker] = frame
        except Exception as exc:
            print(f"Calibration: skipped {ticker} ({exc})")

    if len(frames) < 4:
        return {"available": False, "note": "Not enough price data could be downloaded right now. Try again in a few minutes."}

    all_dates = sorted(set().union(*[set(f.index) for f in frames.values()]))
    split_date = all_dates[int(len(all_dates) * TRAIN_FRACTION)]
    purge_date = split_date - pd.Timedelta(days=PURGE_DAYS)

    train = pd.concat([f[f.index < purge_date] for f in frames.values()])
    y_train = (train["future_return"] > 0).astype(int)

    model = xgb.XGBClassifier(
        n_estimators=200, max_depth=4, learning_rate=0.05,
        subsample=0.8, colsample_bytree=0.8, eval_metric="logloss",
    )
    model.fit(train[FEATURES], y_train)

    test = pd.concat([f[f.index >= split_date] for f in frames.values()])
    proba = model.predict_proba(test[FEATURES])[:, 1]
    outcome = (test["future_return"] > 0).astype(int).values
    n_total = len(outcome)

    base_rate = float(y_train.mean())
    brier_model = float(np.mean((proba - outcome) ** 2))
    brier_base = float(np.mean((base_rate - outcome) ** 2))

    bins = []
    ece = 0.0
    for lo, hi in zip(BIN_EDGES[:-1], BIN_EDGES[1:]):
        mask = (proba >= lo) & (proba < hi)
        n = int(mask.sum())
        if n == 0:
            bins.append({
                "label": _label(lo, hi), "lower_pct": round(lo * 100, 1),
                "upper_pct": round(min(hi, 1.0) * 100, 1), "count": 0,
                "predicted_pct": None, "actual_pct": None, "reliable": False,
            })
            continue
        pred = float(proba[mask].mean())
        act = float(outcome[mask].mean())
        ece += (n / n_total) * abs(pred - act)
        bins.append({
            "label": _label(lo, hi), "lower_pct": round(lo * 100, 1),
            "upper_pct": round(min(hi, 1.0) * 100, 1), "count": n,
            "predicted_pct": round(pred * 100, 1), "actual_pct": round(act * 100, 1),
            "reliable": n >= MIN_BIN_COUNT,
        })

    result = {
        "available": True,
        "n_predictions": int(n_total),
        "n_tickers": int(len(frames)),
        "test_start": str(test.index.min().date()),
        "test_end": str(test.index.max().date()),
        "base_rate_pct": round(base_rate * 100, 1),
        "ece_pct": round(ece * 100, 1),
        "brier_model": round(brier_model, 4),
        "brier_baseline": round(brier_base, 4),
        "bins": bins,
        "notes": [
            "A fresh model was trained only on data before the test period, with a gap to prevent label overlap, then scored on the later period it never saw.",
            "Consecutive days share overlapping 5-day outcomes, so the real number of independent observations is smaller than the counts shown.",
            "The live model is trained on more recent data than this test model, so this is a close approximation of its reliability, not an exact measurement.",
        ],
    }
    set_cache(CACHE_KEY, result)
    return result