import pandas as pd
import yfinance as yf

from app.data.cache import get_cached, set_cache

SHOCKS = [
    {"name": "2018 Q4 sell-off", "start": "2018-09-20", "end": "2018-12-24"},
    {"name": "COVID-19 crash", "start": "2020-02-19", "end": "2020-03-23"},
    {"name": "2022 rate-hike bear market", "start": "2022-01-03", "end": "2022-10-13"},
]
HISTORY_START = "2018-01-01"


def _clean_close(ticker):
    raw = yf.Ticker(ticker).history(start=HISTORY_START)
    if raw is None or raw.empty:
        return None
    raw = raw.dropna(subset=["Close"])
    idx = pd.to_datetime(raw.index)
    if idx.tz is not None:
        idx = idx.tz_localize(None)
    close = pd.Series(raw["Close"].values, index=idx.normalize())
    close = close[~close.index.duplicated(keep="last")].sort_index()
    return close if len(close) > 0 else None


def _analyze_window(close, start, end):
    start_ts, end_ts = pd.Timestamp(start), pd.Timestamp(end)
    if close.index[0] > start_ts + pd.Timedelta(days=7):
        return None

    w = close[(close.index >= start_ts) & (close.index <= end_ts)]
    if len(w) < 5:
        return None

    drawdown = w / w.cummax() - 1.0
    trough_date = drawdown.idxmin()
    max_dd = float(drawdown.min())
    peak_value = float(w.loc[:trough_date].max())

    after = close[close.index > trough_date]
    mask = after >= peak_value
    if mask.any():
        rec_date = mask.idxmax()
        recovery_days = int(len(after.loc[:rec_date]))
        recovered = True
    else:
        recovery_days = None
        recovered = False

    return {
        "drawdown_pct": round(max_dd * 100, 1),
        "trough_date": str(trough_date.date()),
        "recovered": recovered,
        "recovery_days": recovery_days,
    }


def run_stress_test(resolved_ticker: str) -> dict:
    cache_key = f"stress_{resolved_ticker}".replace("^", "_")
    cached = get_cached(cache_key, max_age_seconds=7 * 86400)
    if cached is not None:
        return cached

    is_india = resolved_ticker.endswith(".NS") or resolved_ticker.endswith(".BO")
    bench_symbol = "^NSEI" if is_india else "SPY"
    bench_label = "Nifty 50" if is_india else "S&P 500 (SPY)"

    try:
        stock = _clean_close(resolved_ticker)
        bench = _clean_close(bench_symbol)
    except Exception as exc:
        return {"available": False, "note": f"Price history could not be downloaded right now ({exc})."}

    if stock is None or bench is None:
        return {"available": False, "note": "Price history was not available for this stock or its benchmark."}

    windows = []
    for shock in SHOCKS:
        s = _analyze_window(stock, shock["start"], shock["end"])
        b = _analyze_window(bench, shock["start"], shock["end"])
        row = {"name": shock["name"], "start": shock["start"], "end": shock["end"], "covered": s is not None and b is not None}
        if row["covered"]:
            row.update({
                "stock_drawdown_pct": s["drawdown_pct"],
                "benchmark_drawdown_pct": b["drawdown_pct"],
                "trough_date": s["trough_date"],
                "recovered": s["recovered"],
                "recovery_days": s["recovery_days"],
            })
        windows.append(row)

    covered = [w for w in windows if w["covered"]]
    if covered:
        deeper = sum(1 for w in covered if w["stock_drawdown_pct"] < w["benchmark_drawdown_pct"])
        summary = f"In {len(covered)} past market shock{'s' if len(covered) != 1 else ''}, this stock fell more than {bench_label} in {deeper}."
    else:
        summary = "This stock's price history does not overlap any of the stress windows."

    result = {
        "available": True,
        "benchmark_label": bench_label,
        "windows": windows,
        "summary": summary,
        "note": "Drawdown is the largest peak-to-trough fall inside each window. Recovery counts trading days from the trough until the pre-trough peak was regained. These are historical facts, not predictions.",
    }
    set_cache(cache_key, result)
    return result