from sqlalchemy import Column, Integer, String, true
from database import Base
from sqlalchemy import Column,Integer,Float,String,ForeignKey,DateTime
from sqlalchemy.orm import relationship
from database import Base
from sqlalchemy import Boolean
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    first_name = Column(String)
    last_name = Column(String)
    mobile = Column(String)
    country = Column(String)
    state = Column(String)
    city = Column(String)
    zip_code = Column(String)
    date_of_birth = Column(String)
    referral_code = Column(String,unique=True,index=True)
    referred_by = Column(String,nullable=True)
    wallet = relationship("Wallet",back_populates="user")


class Wallet(Base):
    __tablename__ = "wallets"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    balance = Column(Float,default=0)
    available_balance = Column(Float,default=0)
    margin_used = Column(Float,default=0)
    floating_pl = Column(Float,default=0)
    equity = Column(Float,default=0)
    currency = Column(String,default="USDT")
    bonus = Column(Float,default=0)
    is_first_deposit = Column(Boolean,default=True)
    user = relationship("User",back_populates="wallet")
class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"),nullable=False)
    type = Column(String)
    amount = Column(Float)
    description = Column(String)
    currency = Column(String,default="USDT")
    created_at = Column(DateTime,default=datetime.utcnow)
    user = relationship("User")
class Trade(Base):
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    symbol = Column(String, nullable=False)          # EURUSD, BTCUSDT
    direction = Column(String, nullable=False)       # UP / DOWN
    amount = Column(Float, nullable=False)

    entry_price = Column(Float, nullable=False)
    exit_price = Column(Float, nullable=True)

    payout_percent = Column(Float, default=80.0)
    profit = Column(Float, default=0.0)

    status = Column(String, default="OPEN")          # OPEN / WON / LOST / DRAW / CANCELLED

    account_type = Column(String, default="DEMO")    # DEMO / REAL
    duration = Column(Integer, nullable=False)       # seconds

    opened_at = Column(DateTime, default=datetime.utcnow)
    expiry_time = Column(DateTime, nullable=False)
    closed_at = Column(DateTime, nullable=True)

    is_settled = Column(Boolean, default=False)

    user = relationship("User")





