from datetime import datetime,timedelta
otp_storage = {}
def store_otp(email,otp):
    expiry_time = datetime.utcnow() + timedelta(minutes=10)
    otp_storage[email] = {
        "otp": otp,
        "expiry": expiry_time
    }