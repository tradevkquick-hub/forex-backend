from celery_worker import celery
import time
from database import SessionLocal
from models import User, Trade,Wallet
from utils import get_live_price

@celery.task
def close_trade(trade_id: int,duration: int):
    time.sleep(duration)
    db = SessionLocal()
    trade = db.query(Trade).filter(Trade.id == trade_id).first()
    if not trade or trade.status != "open":
        db.close()
        return
    wallet = db.query(Wallet).filter(Wallet.user_id == trade.user_id).first()
    exit_price = get_live_price(trade.asset)
    print("ENTRY:",trade.entry_price)
    print("EXIT:",exit_price)
    print("DIFF:",exit_price-trade.entry_price)
    print("DIRECTION:",trade.direction)
    if trade.direction == "BUY":
        win = exit_price > trade.entry_price
    elif trade.direction == "SELL":
        win = exit_price < trade.entry_price

    else:
        win = False
    if win:
        profit = trade.amount * 0.8
        wallet.available_balance +=trade.amount+profit
        trade.status = "win"
        trade.profit = profit
    else:
        trade.status = "loss"
        trade.profit = -trade.amount
    trade.exit_price = exit_price
    db.commit()
    db.close()