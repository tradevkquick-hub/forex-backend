from typing import Optional

from pydantic import BaseModel, EmailStr, validator
from datetime import date

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    confirm_password: str
    referral_code: str | None = None

    @validator("confirm_password")
    def passwords_match(cls, v, values):
        if "password" in values and v != values["password"]:
            raise ValueError("Passwords do not match")
        return v
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class VerifyOTP(BaseModel):
    email: EmailStr
    otp: str

class UpdateProfile(BaseModel):
    first_name:Optional[str] = None
    last_name:Optional[str] = None
    mobile:Optional[str] = None
    country:Optional[str] = None
    state:Optional[str] = None
    city:Optional[str] = None
    zip_code:Optional[str] = None
    date_of_birth:Optional[date] = None



class ForgotPassword(BaseModel):
    email: EmailStr
class VerifyResetOTP(BaseModel):
    email: EmailStr
    otp: str
class ResetPassword(BaseModel):
    email: EmailStr
    new_password: str
class WalletResponse(BaseModel):
    balance: float
    available_balance: float
    margin_used: float
    floating_pl : float
    equity : float
    currency : str



    # Always include this for SQLAlchemy compatibility




