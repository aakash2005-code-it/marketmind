import numpy as np
import pandas as pd
import yfinance as yf
import xgboost as xgb

from app.data.cache import get_cached, set_cache
from app.scoring.technical_ml import _build_features, FEATURES

BASKET = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "V", "WMT", "JNJ", "KO"]
HORIZON_DAYS = 5
TRAIN_FRACTION = 0.6
PURGE_DAYS = 8
BUY_THRESHOLD = 0.55
AVOID_THRESHOLD = 0.45
CACHE_KEY = "track_record_v1"


def _num(value, digits=2):
    if value is None:
        return None
    try:
        v = float(value)
    except (TypeError, ValueError):
        return None
    if np.isnan(v) or np.isinf(v):
        return None
    return round(v, digits)


def _load_ticker_frame(ticker: str):
    raw = yf.Ticker(ticker).history(period="10y")
    if raw is None or raw.empty or len(raw) < 300:
        return None

    raw = raw.dropna(subset=["Close"])
    idx = pd.to_datetime(raw.index)
    if idx.tz is not None:
        idx = idx.tz_localize(None)
    raw.index = idx.normalize()

    feat = _build_features(raw)
    feat["future_return"] = feat["Close"].shift(-HORIZON_DAYS) / feat["Close"] - 1
    feat = feat.dropna(subset=FEATURES + ["future_return"])
    return feat[FEATURES + ["future_return"]]


def run_track_record(force: bool = False) -> dict:
    if not force:
        cached = get_cached(CACHE_KEY, max_age_seconds=86400)
        if cached is not None:
            return cached

    frames = {}
    for ticker in BASKET:
        try:
            frame = _load_ticker_frame(ticker)
            if frame is not None:
                frames[ticker] = frame
        except Exception as exc:
            print(f"Track record: skipped {ticker} ({exc})")

    if len(frames) < 4:
        return {
            "available": False,
            "note": "Not enough price data could be downloaded right now. Try again in a few minutes.",
        }

    all_dates = sorted(set().union(*[set(f.index) for f in frames.values()]))
    split_date = all_dates[int(len(all_dates) * TRAIN_FRACTION)]
    purge_date = split_date - pd.Timedelta(days=PURGE_DAYS)

    train = pd.concat([f[f.index < purge_date] for f in frames.values()])
    X_train = train[FEATURES]
    y_train = (train["future_return"] > 0).astype(int)

    model = xgb.XGBClassifier(
        n_estimators=200,
        max_depth=4,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        eval_metric="logloss",
    )
    model.fit(X_train, y_train)

    # Non-overlapping 5-day holding periods on a shared calendar
    test_dates = [d for d in all_dates if d >= split_date]
    rebalance_dates = pd.Index(test_dates[::HORIZON_DAYS])

    hold_returns = {}
    strategy_returns = {}
    records = []

    for ticker, frame in frames.items():
        test = frame[frame.index >= split_date]
        if test.empty:
            continue

        proba = model.predict_proba(test[FEATURES])[:, 1]
        signal = pd.Series(
            np.where(proba > BUY_THRESHOLD, 1, np.where(proba < AVOID_THRESHOLD, -1, 0)),
            index=test.index,
        )

        sampled_dates = test.index.intersection(rebalance_dates)
        if len(sampled_dates) == 0:
            continue

        sampled_ret = test.loc[sampled_dates, "future_return"]
        sampled_sig = signal.loc[sampled_dates]

        hold_returns[ticker] = sampled_ret
        strategy_returns[ticker] = sampled_ret.where(sampled_sig == 1, 0.0)
        records.append(pd.DataFrame({"signal": sampled_sig.values, "ret": sampled_ret.values}))

    if not records:
        return {"available": False, "note": "No test-period data was available."}

    recs = pd.concat(records, ignore_index=True)
    hold_ret = pd.DataFrame(hold_returns).sort_index().mean(axis=1, skipna=True)
    strat_ret = pd.DataFrame(strategy_returns).sort_index().mean(axis=1, skipna=True)

    hold_curve = (1 + hold_ret).cumprod() * 100
    strat_curve = (1 + strat_ret).cumprod() * 100

    buys = recs[recs["signal"] == 1]
    avoids = recs[recs["signal"] == -1]

    equity_curve = [
        {
            "date": str(d.date()),
            "strategy": _num(strat_curve.loc[d]),
            "buy_hold": _num(hold_curve.loc[d]),
        }
        for d in strat_curve.index
    ]

    result = {
        "available": True,
        "n_tickers": int(len(frames)),
        "horizon_days": HORIZON_DAYS,
        "train_end": str(purge_date.date()),
        "test_start": str(hold_ret.index[0].date()),
        "test_end": str(hold_ret.index[-1].date()),
        "buy_threshold": BUY_THRESHOLD,
        "avoid_threshold": AVOID_THRESHOLD,
        "signals": {
            "buy": int(len(buys)),
            "avoid": int(len(avoids)),
            "hold": int((recs["signal"] == 0).sum()),
        },
        "buy_hit_rate_pct": _num((buys["ret"] > 0).mean() * 100, 1) if len(buys) else None,
        "baseline_up_rate_pct": _num((recs["ret"] > 0).mean() * 100, 1),
        "avg_return_after_buy_pct": _num(buys["ret"].mean() * 100) if len(buys) else None,
        "avg_return_after_avoid_pct": _num(avoids["ret"].mean() * 100) if len(avoids) else None,
        "avg_return_all_pct": _num(recs["ret"].mean() * 100),
        "strategy_total_return_pct": _num(strat_curve.iloc[-1] - 100),
        "buy_hold_total_return_pct": _num(hold_curve.iloc[-1] - 100),
        "equity_curve": equity_curve,
        "notes": [
            "The model behind this test was trained only on data before the test period, with a gap to prevent label overlap, so the test period is genuinely out-of-sample.",
            "Only the technical signal is backtested. Point-in-time fundamentals and news sentiment are not available from the free data sources, so the full three-signal verdict cannot be replayed honestly.",
            "Positions are held for 5 trading days at a time, equal-weighted across the basket, with cash when there is no Buy signal. Transaction costs and taxes are ignored.",
            "The basket is large-cap US stocks that exist today, so survivorship bias applies. Past performance does not predict future results.",
        ],
    }

    set_cache(CACHE_KEY, result)
    return results