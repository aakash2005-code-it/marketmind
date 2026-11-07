import yfinance as yf
from app.data.fundamentals_data import get_fundamentals
from app.scoring.diversification import DEFAULT_BASKET
from app.data.indian_markets import INDIA_PEER_MAP

# Curated peer sets for common US tickers
PEER_MAP = {
    "AAPL": ["MSFT", "GOOGL"],
    "MSFT": ["AAPL", "GOOGL"],
    "GOOGL": ["META", "MSFT"],
    "AMZN": ["WMT", "HD"],
    "TSLA": ["GM", "F"],
    "META": ["GOOGL", "DIS"],
    "NVDA": ["AMD", "INTC"],
    "JPM": ["BAC", "V"],
    "V": ["JPM", "BAC"],
    "WMT": ["KO", "PG"],
    "JNJ": ["PFE", "KO"],
    "PFE": ["JNJ", "KO"],
    "XOM": ["JPM", "WMT"],
    "KO": ["WMT", "PG"],
    "DIS": ["META", "GOOGL"],
    "BAC": ["JPM", "V"],
}
# Merge Indian peers
PEER_MAP.update(INDIA_PEER_MAP)


def _get_peer_tickers(ticker: str, sector: str | None) -> list[str]:
    ticker = ticker.upper()
    if ticker in PEER_MAP:
        return PEER_MAP[ticker]

    # Fallback: pick 2 tickers from the same sector in the default basket
    if sector:
        same_sector = [t for t, s in DEFAULT_BASKET.items() if s == sector and t != ticker]
        if same_sector:
            return same_sector[:2]

    return []


def _peer_metrics(ticker: str) -> dict | None:
    try:
        fundamentals = get_fundamentals(ticker)
        hist = yf.Ticker(ticker).history(period="1y")
        if hist.empty:
            return None
        one_year_return = round(((hist["Close"].iloc[-1] / hist["Close"].iloc[0]) - 1) * 100, 2)

        return {
            "ticker": ticker,
            "company_name": fundamentals.get("company_name") or ticker,
            "pe_ratio": fundamentals.get("pe_ratio"),
            "one_year_return_pct": one_year_return,
        }
    except Exception:
        return None


def get_peers(ticker: str, sector: str | None) -> dict:
    peer_tickers = _get_peer_tickers(ticker, sector)
    peers = []
    for t in peer_tickers:
        m = _peer_metrics(t)
        if m:
            peers.append(m)

    return {"peers": peers}