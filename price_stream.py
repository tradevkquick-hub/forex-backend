import time
import random
from redis_client import r
import firebase_admin
from firebase_admin import firestore
from firebase_config import db
price = 1.0800
trend = 0
while True:
    if random.random() < 0.1:
        trend = random.choice([-0.0002,0.0002])
    move = random.uniform(-0.0003,0.0003) + trend
    price += move
    price = round(price,5)
    db.collection('prices').document("EURUSD").set({
        "price": price,
        "timestamp": firestore.SERVER_TIMESTAMP
    })
    print("live Price :",price)
    time.sleep(1)