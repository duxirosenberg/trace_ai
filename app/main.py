# app/main.py
from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from app import db, models, schemas, crud
from app.db import SessionLocal, init_db
from app.auth import verify_password
from app.utils.csv_processor import parse_csv
from typing import List
import json
from fastapi.middleware.cors import CORSMiddleware

# Initialize the database and create tables if they do not exist
init_db()

app = FastAPI(title="Personal Finance Tracker POC")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins, you can specify a list of allowed origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

# Dependency to provide a database session for each request
def get_db():
    db_session = SessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()

@app.get("/")
def read_root():
    return {"message": "Welcome to the Personal Finance Tracker API POC"}

# --- User Endpoints ---
@app.post("/users/", response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    return crud.create_user(db=db, user=user)

@app.post("/login", response_model=schemas.Token)
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if not db_user or not verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    # For this POC, we return a dummy token. In production, use JWT or similar.
    return {"access_token": f"fake-token-for-user-{db_user.id_user}", "token_type": "bearer"}

@app.get("/users", response_model=List[schemas.UserResponse])
def list_users(db: Session = Depends(get_db)):
    return crud.get_all_users(db)

# --- Bank Account Endpoints ---
@app.post("/accounts/", response_model=schemas.BankAccountResponse)
def create_bank_account(account: schemas.BankAccountCreate, db: Session = Depends(get_db)):
    return crud.create_bank_account(db=db, account=account)

@app.delete("/accounts/{id_bank_account}", response_model=schemas.BankAccountResponse)
def delete_bank_account(id_bank_account: int, db: Session = Depends(get_db)):
    account = crud.delete_bank_account(db, id_bank_account)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account

@app.get("/users/{id_user}/accounts", response_model=list[schemas.BankAccountResponse])
def list_accounts_for_user(id_user: int, db: Session = Depends(get_db)):
    accounts = crud.get_accounts_by_user(db, id_user)
    return accounts

# --- Transaction Endpoints ---
@app.post("/transactions/", response_model=schemas.TransactionResponse)
def create_transaction(transaction: schemas.TransactionBase, db: Session = Depends(get_db)):
    return crud.create_transaction(db, transaction)

@app.get("/transactions/", response_model=list[schemas.TransactionResponse])
def list_transactions(id_bank_account: int = None, db: Session = Depends(get_db)):
    transactions = crud.get_transactions(db, id_bank_account)
    return transactions

@app.get("/transactions/{id_transaction}", response_model=schemas.TransactionResponse)
def read_transaction(id_transaction: int, db: Session = Depends(get_db)):
    db_transaction = crud.get_transaction(db, id_transaction)
    if not db_transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return db_transaction

@app.put("/transactions/{id_transaction}", response_model=schemas.TransactionResponse)
def update_transaction(id_transaction: int, transaction: schemas.TransactionBase, db: Session = Depends(get_db)):
    db_transaction = crud.update_transaction(db, id_transaction, transaction)
    if not db_transaction:
        raise HTTPException(status_code=404, detail="Transaction update failed")
    return db_transaction

@app.delete("/transactions/{id_transaction}", response_model=schemas.TransactionResponse)
def delete_transaction(id_transaction: int, db: Session = Depends(get_db)):
    db_transaction = crud.delete_transaction(db, id_transaction)
    if not db_transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return db_transaction



@app.post("/accounts/{id_bank_account}/upload_csv_advanced")
async def upload_csv_advanced(
    id_bank_account: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Check if the bank account exists
    account = crud.get_bank_account(db, id_bank_account)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    # Save the uploaded file temporarily
    temp_file_path = f"/tmp/{file.filename}"
    with open(temp_file_path, "wb") as f:
        f.write(await file.read())

    try:
        transactions_df = parse_csv(temp_file_path)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # Process DataFrame rows to create transactions in the DB, similar to previous logic.
    created_transactions = []
    for _, row in transactions_df.iterrows():
        transaction_data = {
            "id_bank_account": id_bank_account,
            "date": row["date"],
            "amount": row["amount"],
            "currency": row["currency"] if row["currency"] else account.user.preferred_currency,  
            "description": row["description"],
            "recipient": row["recipient"],
            "raw_data": row["raw_data"],
        }
        print(transaction_data)
        print("\n")
        transaction_schema = schemas.TransactionBase(**transaction_data)
        transaction = crud.create_transaction(db, transaction_schema)
        created_transactions.append(transaction)

    
    return {"created_transactions": created_transactions}
