import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
from app.data.cache import get_cached, set_cache

load_dotenv()
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")

def get_recent_headlines(ticker: str, company_name: str = None, days: int = 7) -> list[str]:
    cache_key = f"news_{ticker}_{days}d"
    cached = get_cached(cache_key, max_age_seconds=21600)  # 6 hours
    if cached is not None:
        return cached

    query = f'"{company_name}" AND (stock OR shares OR earnings OR revenue)' if company_name else ticker
    from_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

    url = "https://newsapi.org/v2/everything"
    params = {
        "q": query,
        "from": from_date,
        "sortBy": "publishedAt",
        "language": "en",
        "apiKey": NEWSAPI_KEY,
        "pageSize": 20,
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()

        if data.get("status") != "ok":
            raise ValueError(f"NewsAPI error: {data.get('message')}")

        headlines = [article["title"] for article in data.get("articles", []) if article.get("title")]

    except Exception as e:
        print(f"News fetch failed ({e}), returning empty list")
        headlines = []

    set_cache(cache_key, headlines)
    return headlines