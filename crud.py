from sqlalchemy.orm import Session
from passlib.hash import bcrypt
from models import User
from schemas import UserRegister
from models import Wallet
from utils import generate_referral_code

def create_user(user: UserRegister, db: Session):
    hashed_password = bcrypt.hash(user.password)
    new_referral_code = generate_referral_code()

    db_user = User(
        email=user.email,
        password=hashed_password,
        referral_code=new_referral_code
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user
def authenticate_user(email: str,password: str,db:Session):
    user =db.query(User).filter(User.email == email).first()
    if not user:
        return None
    if not bcrypt.verify(password,user.password):
        return None
    return user
def create_wallet(db,user_id):
    wallet = Wallet(
        user_id=user_id,
        balance=0,
        available_balance=0,
        margin_used=0,
        floating_pl=0,
        equity=0
    )
    db.add(wallet)
    db.commit()
    db.refresh(wallet)
    return wallet

