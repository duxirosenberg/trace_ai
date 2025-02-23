# app/crud.py
from sqlalchemy.orm import Session
from app import models, schemas
from app.auth import get_password_hash

# --- User CRUD ---
def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        name=user.name,
        password_hash=hashed_password,
        preferred_currency=user.preferred_currency
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_all_users(db: Session):
    return db.query(models.User).all()


# --- Bank Account CRUD ---
def create_bank_account(db: Session, account: schemas.BankAccountCreate):
    db_account = models.BankAccount(
        id_user=account.id_user,
        account_name=account.account_name,
        account_number=account.account_number,
        bank_name=account.bank_name
    )
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account

def get_bank_account(db: Session, id_bank_account: int):
    return db.query(models.BankAccount).filter(models.BankAccount.id_bank_account == id_bank_account).first()

def delete_bank_account(db: Session, id_bank_account: int):
    account = get_bank_account(db, id_bank_account)
    if account:
        db.delete(account)
        db.commit()
    return account

def get_accounts_by_user(db: Session, id_user: int):
    return db.query(models.BankAccount).filter(models.BankAccount.id_user == id_user).all()

# --- Transaction CRUD ---
def create_transaction(db: Session, transaction: schemas.TransactionBase):
    db_transaction = models.Transaction(
        id_bank_account=transaction.id_bank_account,
        date=transaction.date,
        amount=transaction.amount,
        currency=transaction.currency,
        description=transaction.description,
        recipient=transaction.recipient,
        raw_data=transaction.raw_data
    )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

def get_transaction(db: Session, id_transaction: int):
    return db.query(models.Transaction).filter(models.Transaction.id_transaction == id_transaction).first()

def get_transactions(db: Session, id_bank_account: int = None):
    query = db.query(models.Transaction)
    if id_bank_account:
        query = query.filter(models.Transaction.id_bank_account == id_bank_account)
    print(f"Transactions for account {id_bank_account}: {query.all()}")  # Log the transactions
    return query.all()

def delete_transaction(db: Session, id_transaction: int):
    db_transaction = get_transaction(db, id_transaction)
    if db_transaction:
        db.delete(db_transaction)
        db.commit()
    return db_transaction
