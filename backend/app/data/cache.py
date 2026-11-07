import json
import time
import os

CACHE_DIR = "cache"
os.makedirs(CACHE_DIR, exist_ok=True)

def get_cached(key: str, max_age_seconds: int):
    path = f"{CACHE_DIR}/{key}.json"
    if os.path.exists(path):
        age = time.time() - os.path.getmtime(path)
        if age < max_age_seconds:
            with open(path) as f:
                return json.load(f)
    return None

def set_cache(key: str, data: dict):
    path = f"{CACHE_DIR}/{key}.json"
    with open(path, "w") as f:
        json.dump(data, f)