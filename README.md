To make this work, you need ollama with the llama3:8b model installed. 

project/
├── app/
│   ├── __init__.py      # Makes 'app' a package (can be empty)
│   ├── db.py            # Database connection & initialization
│   ├── models.py        # SQLAlchemy models (User, BankAccount, Transaction, Label)
│   ├── schemas.py       # Pydantic models for request/response validation
│   ├── crud.py          # CRUD helper functions for DB operations
│   ├── auth.py          # Authentication utilities (password hashing, etc.)
│   └── main.py          # FastAPI application & route definitions
