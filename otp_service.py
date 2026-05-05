import random
from datetime import datetime,timedelta

reset_otp_storage = {}
def generate_reset_otp(email):
    otp = str(random.randint(100000,999999))
    reset_otp_storage[email] = {
        "otp": otp,
        "expiry": datetime.utcnow() + timedelta(minutes=5)
    }
    return otp

def verify_reset_otp(email,otp):
    record = reset_otp_storage.get(email)
    if not record:
        return False
    if datetime.utcnow() > record["expiry"]:
        return False
    return record["otp"] == otp