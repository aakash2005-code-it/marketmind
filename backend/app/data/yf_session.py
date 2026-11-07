"""
yf_session.py
A shared requests.Session for yfinance that bypasses curl_cffi,
which has DNS resolution issues on some Windows setups with yfinance 1.7+.
"""
import requests

def get_yf_session() -> requests.Session:
    """Return a requests.Session with a browser-like User-Agent."""
    session = requests.Session()
    session.headers.update({
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    })
    return session
