from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.data.technical_data import get_price_history
from app.data.fundamentals_data import get_fundamentals
from app.data.news_data import get_recent_headlines
from app.scoring.technical_ml import technical_score_ml
from app.scoring.fundamentals import fundamentals_score
from app.scoring.signal_conflict import detect_signal_conflict
from app.scoring.stress_test import run_stress_test
from app.scoring.calibration import run_calibration
from app.scoring.sentiment import sentiment_score
from app.ensemble.combiner import combine_scores
from app.auth.routes import router as auth_router
from sqlalchemy.orm import Session
from app.db.database import get_db, Base, engine
from app.db import models
from app.db.models import SearchHistory, User
from app.auth.dependencies import get_current_user
from app.data.ticker_search import search_ticker
from app.scoring.peers import get_peers
from app.scoring.financials import get_quarterly_financials
from app.chat.gemini_client import get_chat_response
from app.models.chat_schemas import ChatRequest
from app.scoring.diversification import build_diversified_recommendations
from app.scoring.headline_sentiment import headline_attribution
from app.scoring.counterfactual import compute_counterfactuals
from app.scoring.track_record import run_track_record
from app.watchlist.routes import router as watchlist_router
from app.data.indian_markets import (
    resolve_indian_ticker, get_currency_symbol, is_indian_ticker,
    INDIAN_TAPE_SYMBOLS,
)
import yfinance as yf
import pandas as pd

import math
import numpy as np


def sanitize_nan(obj):
    if isinstance(obj, dict):
        return {k: sanitize_nan(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [sanitize_nan(x) for x in obj]
    elif isinstance(obj, (float, np.floating)):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return float(obj)
    return obj


Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(watchlist_router)


@app.get("/search-ticker")
def search_ticker_endpoint(q: str):
    return {"results": search_ticker(q)}


@app.post("/chat")
def chat(payload: ChatRequest):
    reply = get_chat_response(payload.message, payload.stock_context)
    return {"reply": reply}


@app.get("/")
def root():
    return {"status": "MarketMind backend is alive"}


@app.get("/financials/{ticker}")
def financials(ticker: str):
    resolved = resolve_indian_ticker(ticker)
    return sanitize_nan(get_quarterly_financials(resolved))


@app.get("/peers/{ticker}")
def peers(ticker: str, sector: str = None):
    resolved = resolve_indian_ticker(ticker)
    return sanitize_nan(get_peers(resolved, sector))


@app.get("/track-record")
def track_record(
    refresh: bool = False,
    current_user: User = Depends(get_current_user),
):
    try:
        return sanitize_nan(run_track_record(force=refresh))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/stress-test/{ticker}")
def stress_test(ticker: str):
    try:
        resolved = resolve_indian_ticker(ticker)
        return sanitize_nan(run_stress_test(resolved))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/calibration")
def calibration(
    refresh: bool = False,
    current_user: User = Depends(get_current_user),
):
    try:
        return sanitize_nan(run_calibration(force=refresh))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/analyze/{ticker}")
def analyze(
    ticker: str,
    company_name: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        # Resolve Indian ticker (for example "Reliance" becomes "RELIANCE.NS")
        resolved_ticker = resolve_indian_ticker(ticker)
        currency_symbol = get_currency_symbol(resolved_ticker)
        indian = is_indian_ticker(resolved_ticker)

        df = get_price_history(resolved_ticker)
        if df is not None and not df.empty:
            df = df.dropna(subset=["Close"])

        fundamentals = get_fundamentals(resolved_ticker)
        headlines = get_recent_headlines(resolved_ticker, company_name)

        tech = technical_score_ml(df)
        fund = fundamentals_score(fundamentals)
        sent = sentiment_score(headlines)

        result = combine_scores(tech, fund, sent)
        result["ticker"] = resolved_ticker
        result["original_ticker"] = ticker.upper()

        valid_closes = df["Close"].dropna() if df is not None and not df.empty else []
        latest_p = float(valid_closes.iloc[-1]) if len(valid_closes) > 0 else 0.0
        result["latest_price"] = round(latest_p, 2)
        result["currency_symbol"] = currency_symbol
        result["is_indian"] = indian
        result["market"] = "NSE/BSE (India)" if indian else "US Markets"
        result["company_name"] = fundamentals.get("company_name")
        result["description"] = fundamentals.get("description")
        result["sector"] = fundamentals.get("sector")
        result["market_cap"] = fundamentals.get("market_cap")
        result["week52_high"] = fundamentals.get("week52_high")
        result["week52_low"] = fundamentals.get("week52_low")
        result["pb_ratio"] = fundamentals.get("pb_ratio")
        result["eps"] = fundamentals.get("eps")
        result["peg_ratio"] = fundamentals.get("peg_ratio")
        result["profit_margin"] = fundamentals.get("profit_margin")
        result["dividend_yield"] = fundamentals.get("dividend_yield")
        result["pe_ratio"] = fundamentals.get("pe_ratio")

        # Trust / data-completeness score
        data_points = {
            "P/E Ratio": fundamentals.get("pe_ratio") is not None,
            "Debt-to-Equity": fundamentals.get("debt_to_equity") is not None,
            "Sector": fundamentals.get("sector") is not None,
            "News Headlines": len(headlines) > 0,
            "Price History": df is not None and not df.empty,
        }
        available = sum(1 for v in data_points.values() if v)
        total = len(data_points)
        result["trust_score"] = {
            "available": available,
            "total": total,
            "percentage": round((available / total) * 100),
            "breakdown": data_points,
        }
         # Raw technical probability (used for the reliability panel) and signal conflict check
        result["technical_probability"] = tech.get("model_probability_up")
        result["signal_conflict"] = detect_signal_conflict(result["breakdown"])

        # Headline-level sentiment attribution
        try:
            result["headline_attribution"] = headline_attribution(headlines)
        except Exception:
            result["headline_attribution"] = []

        # Counterfactual what-if explanations (default 40/30/30 weights)
        try:
            result["counterfactuals"] = compute_counterfactuals(
                df,
                fund["normalized"],
                sent["normalized"],
                (0.4, 0.3, 0.3),
                result["verdict"],
            )
        except Exception:
            result["counterfactuals"] = []

        history_entry = SearchHistory(
            user_id=current_user.id,
            ticker=resolved_ticker,
            verdict=result["verdict"],
            investment_score=result["investment_score"],
            latest_price=result["latest_price"],
        )
        db.add(history_entry)
        db.commit()

        return sanitize_nan(result)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Global ticker tape (US blue-chips)
TICKER_TAPE_SYMBOLS = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "META", "JPM"]


@app.get("/ticker-tape")
def ticker_tape():
    results = []
    for symbol in TICKER_TAPE_SYMBOLS:
        try:
            hist = yf.Ticker(symbol).history(period="2d")
            if len(hist) < 2:
                continue
            prev_close = hist["Close"].iloc[-2]
            last_close = hist["Close"].iloc[-1]
            change_pct = round(((last_close - prev_close) / prev_close) * 100, 2)
            results.append({
                "symbol": symbol,
                "price": round(last_close, 2),
                "change_pct": change_pct,
                "currency": "$",
            })
        except Exception:
            continue
    return {"tape": results}


@app.get("/ticker-tape-india")
def ticker_tape_india():
    """Indian market ticker tape: NIFTY 50, SENSEX, and top NSE stocks."""
    results = []
    for symbol in INDIAN_TAPE_SYMBOLS:
        try:
            hist = yf.Ticker(symbol).history(period="2d")
            if len(hist) < 2:
                continue
            prev_close = hist["Close"].iloc[-2]
            last_close = hist["Close"].iloc[-1]
            change_pct = round(((last_close - prev_close) / prev_close) * 100, 2)
            display_symbol = symbol.replace(".NS", "").replace(".BO", "")
            results.append({
                "symbol": display_symbol,
                "price": round(last_close, 2),
                "change_pct": change_pct,
                "currency": "₹",
                "is_index": symbol.startswith("^"),
            })
        except Exception:
            continue
    return {"tape": results}


@app.get("/portfolio-advisor")
def portfolio_advisor(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_history = (
        db.query(SearchHistory.ticker)
        .filter(SearchHistory.user_id == current_user.id)
        .distinct()
        .all()
    )
    user_tickers = [row[0] for row in user_history]

    result = build_diversified_recommendations(user_tickers=user_tickers)
    return result


@app.get("/my-history")
def my_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    entries = (
        db.query(SearchHistory)
        .filter(SearchHistory.user_id == current_user.id)
        .order_by(SearchHistory.searched_at.desc())
        .limit(50)
        .all()
    )
    return [
        {
            "ticker": e.ticker,
            "verdict": e.verdict,
            "investment_score": e.investment_score,
            "latest_price": e.latest_price,
            "searched_at": e.searched_at.isoformat(),
        }
        for e in entries
    ]


@app.get("/history/{ticker}")
def history(ticker: str):
    try:
        resolved_ticker = resolve_indian_ticker(ticker)
        df = get_price_history(resolved_ticker)
        if df is not None and not df.empty:
            df = df.dropna(subset=["Close"])
        data = []
        if df is not None and not df.empty:
            for idx, row in df.tail(90).iterrows():
                val = row["Close"]
                if pd.notna(val):
                    data.append({"date": str(idx.date()), "close": round(float(val), 2)})
        return {"ticker": resolved_ticker, "history": data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))