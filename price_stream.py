import time
import random
import logging

from redis_client import r


# -----------------------------
# Logging setup
# -----------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


# -----------------------------
# Price settings
# -----------------------------
SYMBOL = "EURUSD"

START_PRICE = 1.08000
MIN_PRICE = 1.05000
MAX_PRICE = 1.12000

PRICE_DECIMALS = 5
UPDATE_INTERVAL_SECONDS = 1


def generate_next_price(current_price: float, current_trend: float):
    """
    Generate next simulated forex price.
    """

    # Sometimes change market trend
    if random.random() < 0.1:
        current_trend = random.choice([-0.0002, 0.0002, 0])

    # Random movement
    movement = random.uniform(-0.0003, 0.0003) + current_trend

    new_price = current_price + movement

    # Keep price inside safe range
    if new_price < MIN_PRICE:
        new_price = MIN_PRICE
        current_trend = 0.0002

    if new_price > MAX_PRICE:
        new_price = MAX_PRICE
        current_trend = -0.0002

    new_price = round(new_price, PRICE_DECIMALS)

    return new_price, current_trend


def save_price_to_redis(symbol: str, price: float):
    """
    Save latest price to Redis.
    /trade API will read this price.
    """
    redis_key = f"price:{symbol.upper()}"
    r.set(redis_key, price)


def start_price_stream():
    price = START_PRICE
    trend = 0

    logging.info(f"Starting Redis price stream for {SYMBOL}")
    logging.info(f"Redis key: price:{SYMBOL}")

    while True:
        try:
            price, trend = generate_next_price(price, trend)

            save_price_to_redis(SYMBOL, price)

            logging.info(f"{SYMBOL} live price: {price}")

            time.sleep(UPDATE_INTERVAL_SECONDS)

        except Exception as e:
            logging.error(f"Price stream error: {e}")
            time.sleep(3)


if __name__ == "__main__":
    start_price_stream()