import os
import redis

REDIS_URL = os.getenv("REDIS_URL")

r = redis.from_url(REDIS_URL, decode_responses=True)


def get_live_price(symbol: str):
    price = r.get(f"price:{symbol.upper()}")

    if price is None:
        return None

    return float(price)