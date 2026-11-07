import os
import requests
import yfinance as yf
from dotenv import load_dotenv
from app.data.cache import get_cached, set_cache

load_dotenv()
ALPHA_VANTAGE_KEY = os.getenv("ALPHA_VANTAGE_KEY")


def _safe_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _fetch_from_alpha_vantage(ticker: str) -> dict:
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "OVERVIEW",
        "symbol": ticker,
        "apikey": ALPHA_VANTAGE_KEY
    }
    response = requests.get(url, params=params, timeout=10)
    data = response.json()

    if not data or "PERatio" not in data:
        raise ValueError("Alpha Vantage returned no usable data")

    return {
        "source": "alpha_vantage",
        "pe_ratio": _safe_float(data.get("PERatio")),
        "debt_to_equity": _safe_float(data.get("DebtToEquity")),
        "sector": data.get("Sector"),
        "market_cap": _safe_float(data.get("MarketCapitalization")),
        "company_name": data.get("Name"),
        "description": data.get("Description"),
        "week52_high": _safe_float(data.get("52WeekHigh")),
        "week52_low": _safe_float(data.get("52WeekLow")),
        "pb_ratio": _safe_float(data.get("PriceToBookRatio")),
        "eps": _safe_float(data.get("EPS")),
        "peg_ratio": _safe_float(data.get("PEGRatio")),
        "profit_margin": _safe_float(data.get("ProfitMargin")),
        "dividend_yield": _safe_float(data.get("DividendYield")),
    }


def _fetch_from_yfinance(ticker: str) -> dict:
    stock = yf.Ticker(ticker)
    info = stock.info

    return {
        "source": "yfinance",
        "pe_ratio": info.get("trailingPE"),
        "debt_to_equity": info.get("debtToEquity"),
        "sector": info.get("sector"),
        "market_cap": info.get("marketCap"),
        "company_name": info.get("longName"),
        "description": info.get("longBusinessSummary"),
        "week52_high": info.get("fiftyTwoWeekHigh"),
        "week52_low": info.get("fiftyTwoWeekLow"),
        "pb_ratio": info.get("priceToBook"),
        "eps": info.get("trailingEps"),
        "peg_ratio": info.get("pegRatio"),
        "profit_margin": info.get("profitMargins"),
        "dividend_yield": info.get("dividendYield"),
    }


def get_fundamentals(ticker: str) -> dict:
    cache_key = f"fundamentals_{ticker}"
    cached = get_cached(cache_key, max_age_seconds=86400)  # 24 hours
    if cached is not None:
        return cached

    data = None
    try:
        data = _fetch_from_alpha_vantage(ticker)
    except Exception as e:
        print(f"Alpha Vantage failed ({e}), falling back to yfinance")

    if data is None:
        try:
            data = _fetch_from_yfinance(ticker)
        except Exception as e:
            print(f"yfinance also failed ({e}), returning empty fundamentals")
            data = {
                "source": "none",
                "pe_ratio": None,
                "debt_to_equity": None,
                "sector": None,
                "market_cap": None,
                "company_name": None,
                "description": None,
                "week52_high": None,
                "week52_low": None,
                "pb_ratio": None,
                "eps": None,
                "peg_ratio": None,
                "profit_margin": None,
                "dividend_yield": None,
            }

    # Validation: flag if critical fields are missing
    data["is_stale_or_incomplete"] = data.get("pe_ratio") is None

    set_cache(cache_key, data)
    return data