import random
import string
from redis_client import r
price_store = {"EURUSD":1.0800}

def generate_referral_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits,k=8))
def get_live_price(asset:str):
    price = r.get(asset)
    if price:
        return float(price)
    return 1.0