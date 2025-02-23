# app/schemas.py
from pydantic import BaseModel, EmailStr
from datetime import datetime, date

# ----- User Schemas -----
class UserBase(BaseModel):
    email: EmailStr = "max.mustermann@example.com"
    name: str = "Max Mustermann"
    preferred_currency: str = "CHF"

class UserCreate(UserBase):
    password: str  = "password" # Plain-text password provided during registration

class UserResponse(UserBase):
    id_user: int
    preferred_currency: str
    created_at: datetime

    class Config:
        orm_mode = True

# Schemas for login
class UserLogin(BaseModel):
    email: EmailStr = "max.mustermann@example.com"
    password: str = "password"

class Token(BaseModel):
    access_token: str
    token_type: str

# ----- Bank Account Schemas -----
class BankAccountBase(BaseModel):
    account_name: str = "CHF Savings"
    account_number: str = "1234567890"
    bank_name: str = "Revolut"

class BankAccountCreate(BankAccountBase):
    id_user: int =1 # In a more advanced setup, this may be derived from the auth token

class BankAccountResponse(BankAccountBase):
    id_bank_account: int
    created_at: datetime

    class Config:
        orm_mode = True

# ----- Transaction Schemas -----
class TransactionBase(BaseModel):
    id_bank_account: int
    date: datetime
    amount: float = 100.00
    currency: str = "CHF"
    description: str = "Food"
    recipient: str = "Peter Müller"
    raw_data: str = "test"


class TransactionResponse(TransactionBase):
    id_transaction: int
    created_at: datetime

    class Config:
        orm_mode = True

# ----- Label Schemas (Optional for later phases) -----
class LabelBase(BaseModel):
    id_transaction: int
    label_name: str

class LabelCreate(LabelBase):
    pass

class LabelResponse(LabelBase):
    id_label: int
    created_at: datetime

    class Config:
        orm_mode = True
