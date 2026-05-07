from fastapi import BackgroundTasks
import time
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from crud import create_user, create_wallet
from database import get_db, Base, engine, SessionLocal
from models import User,Wallet
from schemas import UserRegister, VerifyResetOTP
from passlib.context import CryptContext
from schemas import LoginRequest,VerifyOTP
from crud import authenticate_user
from otp import generate_otp
from otp_store import otp_storage
from fastapi import  HTTPException
from email_service import send_otp_email
from otp_store import store_otp
from datetime import datetime
from otp_store import otp_storage
from auth import create_access_token,create_refresh_token,get_current_user
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer
from schemas import UpdateProfile
from otp_service import generate_reset_otp,verify_reset_otp
from schemas import ForgotPassword,VerifyResetOTP,ResetPassword
from crud import create_wallet
from schemas import WalletResponse
from  utils import generate_referral_code
from models import Transaction
from models import Trade
from datetime import datetime,timedelta
import random
from tasks import close_trade
from fastapi.middleware.cors import CORSMiddleware



app = FastAPI()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create

Base.metadata.create_all(bind=engine)
def get_live_price(asset):
    return random.uniform(90,110)




# Registration endpoint
@app.post("/register")
def register(user:UserRegister,db: Session = Depends(get_db)):
    return {"email":user.email}
@app.post("/login")
def login(user: LoginRequest,db: Session = Depends(get_db)):
    db_user = authenticate_user(user.email, user.password, db)
    if not db_user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    otp = generate_otp()
    store_otp(user.email,otp)
    send_otp_email(user.email, otp)
    return{"message":"OTP sent"}
@app.post("/verify-otp")
def verify_otp(data:VerifyOTP):
    stored_otp = otp_storage.get(data.email)
    if not stored_otp:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    if datetime.utcnow() > stored_otp["expiry"]:
        raise HTTPException(status_code=400, detail="OTP expired")
    if stored_otp["otp"] != data.otp:
        raise HTTPException(status_code=400, detail="Incorrect otp")
    access_token = create_access_token({"sub": data.email})
    refresh_token = create_refresh_token({"email": data.email})
    del otp_storage[data.email]
    return {"message":"Login Successful","access_token":access_token,"refresh_token":refresh_token,"token_type":"Bearer"}
@app.put("/profile")
def update_profile(data: UpdateProfile, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    current_user.first_name = data.first_name
    current_user.last_name = data.last_name
    current_user.mobile = data.mobile
    current_user.country = data.country
    current_user.state = data.state
    current_user.city = data.city
    current_user.zip_code = data.zip_code
    current_user.date_of_birth = data.date_of_birth
    db.commit()
    db.refresh(current_user)
    return {"message":"Profile Updated successfully"}
@app.post("/forgot-password")
def forgot_password(data:ForgotPassword):
    otp = generate_reset_otp(data.email)
    print("Reset OTP:", otp)
    send_otp_email(data.email, otp)
    return {"message":"Password Reset OTP sent successfully"}
@app.post("/verify-reset-otp")
def verify_reset(data:VerifyResetOTP):
    if not verify_reset_otp(data.email,data.otp):
        raise HTTPException(status_code=400, detail="Invalid or Expired OTP")
    return {"message":"OTP verified "}
@app.post("/reset-password")
def reset_password(data: ResetPassword,db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        raise HTTPException(status_code=404,detail="User not found")
    hashed_password = pwd_context.hash(data.new_password)
    user.password = hashed_password
    db.commit()
    return {"message":"Password Reset successfully"}

@app.get("/wallet")
def get_wallet(email:str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return {"message":"User not found"}
    wallet = db.query(Wallet).filter(Wallet.user_id == user.id).first()
    return {
        "balance": wallet.balance,
        "available_balance": wallet.available_balance,
        "bonus": wallet.bonus,
        "margin_used": wallet.margin_used,
        "floating_pl": wallet.floating_pl,
        "equity": wallet.equity,
        "currency": wallet.currency
    }
@app.post("/wallet")
def deposit(email: str,
        amount: float,
        db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return {"message":"User not found"}

    wallet = db.query(Wallet).filter(Wallet.user_id == user.id).first()
    wallet.balance += amount
    wallet.available_balance += amount
    tx = Transaction(user_id=user.id,type="deposit",amount=amount,description="Deposited successfully",currency="USDT")
    db.add(tx)
    bonus_added = 0
    if wallet.is_first_deposit:
        bonus_added = amount * 0.10
        wallet.bonus += bonus_added
        wallet.is_first_deposit = False
        bonus_tx = Transaction(user_id=user.id,type="bonus",amount=bonus_added,description="Bonus added",currency="USDT")
        db.add(bonus_tx)
    wallet.equity = wallet.balance + wallet.floating_pl
    db.commit()
    return {"message":" deposited successfully","deposit":amount,"bonus added":bonus_added}
@app.post("/withdraw")
def withdraw(email: str,amount: float, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return {"message":"User not found"}
    wallet = db.query(Wallet).filter(Wallet.user_id == user.id).first()
    if amount <=0:
        return {"message":"Invalid amount"}
    if amount < 50:
        return {"message":"Minimum Withdraw is 50 USDT"}
    if amount > 9999:
        return {"message":"Maximum Withdraw is 9999 USDT"}
    if wallet.available_balance < amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")
    fee = amount * 0.03
    final_amount =amount - fee
    wallet.balance -= amount
    wallet.available_balance -= amount
    withdraw_tx = Transaction(
        user_id=user.id,
        type="withdraw",
        amount=amount,
        description="Withdraw request",
        currency="USDT"
    )
    fee_tx = Transaction(
        user_id=user.id,
        type="fee",
        amount=fee,
        description="Withdraw fee (3%)",
        currency="USDT"
    )
    db.add(withdraw_tx)
    db.add(fee_tx)
    db.commit()
    return {"message":"Wallet withdraw successfully","Withdraw amount":amount,"fee":fee,"final_amount_sent":final_amount,"remaining_balance":wallet.balance}
@app.get("/transactions")
def get_transactions(email: str,db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return {"message":"User not found"}
    transactions = db.query(Transaction).filter(Transaction.user_id == user.id)\
            .order_by(Transaction.created_at.desc())\
                .all()
    result = []
    for tx in transactions:
        result.append({
            "type": tx.type,
            "amount": tx.amount,
            "description": tx.description,
            "currency":tx.currency,
            "time":tx.created_at
        })
        return result
@app.post("/trade")
def place_trade(email:str,asset:str,direction: str,amount:float,duration:int,background_tasks: BackgroundTasks,db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return {"message":"User not found"}
    wallet = db.query(Wallet).filter(Wallet.user_id == user.id).first()
    if not wallet:
        return {"message":"Wallet not found"}
    if wallet.available_balance < amount:
        return {"message":"Insufficient balance"}
    wallet.available_balance -= amount
    wallet.margin_used += amount
    entry_price = get_live_price(asset)
    print("ENTRY PRICE",entry_price)
    expiry_time = datetime.utcnow() + timedelta(seconds=duration)
    trade = Trade(
        user_id=user.id,
        asset=asset,
        direction=direction,
        amount=amount,
        entry_price=entry_price,
        duration=duration,
        expiry_time=expiry_time,
        payout_percentage=0.8
    )
    db.add(trade)
    db.commit()
    db.refresh(trade)
    close_trade.delay(trade.id,duration)
    return {
        "message":"Trade placed successfully",
        "trade":trade.id,
        "entry_price":entry_price,
        "expiry_time":expiry_time
    }



