# app/models.py
from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db import Base

class User(Base):
    __tablename__ = "users"
    
    id_user = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    preferred_currency = Column(String, default="CHF")
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=func.now())
    
    bank_accounts = relationship("BankAccount", back_populates="user", cascade="all, delete")

class BankAccount(Base):
    __tablename__ = "bank_accounts"
    
    id_bank_account = Column(Integer, primary_key=True, index=True)
    id_user = Column(Integer, ForeignKey("users.id_user", ondelete="CASCADE"), nullable=False)
    account_name = Column(String, nullable=False)
    account_number = Column(String, unique=True, index=True, nullable=False)
    bank_name = Column(String, nullable=False)
    transaction_mapping = Column(JSON, default={})
    transactions_negative_balance = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    
    user = relationship("User", back_populates="bank_accounts")
    transactions = relationship("Transaction", back_populates="account", cascade="all, delete")

class Transaction(Base):
    __tablename__ = "transactions"
    
    id_transaction = Column(Integer, primary_key=True, index=True)
    id_bank_account = Column(Integer, ForeignKey("bank_accounts.id_bank_account", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False, index=True)
    amount = Column(Float, nullable=False)
    currency = Column(String, nullable=False)
    description = Column(String)
    recipient = Column(String, index=True)
    raw_data = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.now())
    
    account = relationship("BankAccount", back_populates="transactions")
    labels = relationship("Label", back_populates="transaction", cascade="all, delete")

class Label(Base):
    __tablename__ = "labels"
    
    id_label = Column(Integer, primary_key=True, index=True)
    id_transaction = Column(Integer, ForeignKey("transactions.id_transaction", ondelete="CASCADE"), nullable=False)
    label_name = Column(String, nullable=False)
    created_at = Column(DateTime, default=func.now())
    
    transaction = relationship("Transaction", back_populates="labels")
