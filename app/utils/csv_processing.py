# app/csv_processor.py
from io import StringIO
import clevercsv
import pandas as pd
import json

def read_csv_file(file) -> pd.DataFrame:
    """
    Reads a CSV file using clevercsv for robust parsing and returns a pandas DataFrame.
    """
    try:
        content = file.read()
        if isinstance(content, bytes):
            content = content.decode("utf-8", errors="replace")
        s = StringIO(content)
        reader = clevercsv.reader(s)
        rows = list(reader)
        if not rows:
            raise ValueError("CSV file is empty.")
        # Assume the first row contains headers
        df = pd.DataFrame(rows[1:], columns=rows[0])
        return df
    except Exception as e:
        raise ValueError(f"Error reading CSV file with clevercsv: {e}")

def get_default_mapping(df: pd.DataFrame) -> dict:
    """
    Returns a default mapping from DataFrame columns to Transaction fields.
    This is a placeholder for later integration with an LLM (e.g., Ollama) to suggest the best mapping.
    
    For now, it assumes the CSV columns are named exactly:
      - date
      - amount
      - description
      - recipient
      - currency
    """
    default_mapping = {
        "date": "date",
        "amount": "amount",
        "description": "description",
        "recipient": "recipient",
        "currency": "currency"
    }
    return default_mapping

# Future implementation: integrate LLM mapping suggestion.
def suggest_transaction_mapping(df: pd.DataFrame, sample_size: int = 3) -> dict:
    """
    Placeholder for LLM-based mapping suggestion.
    In the future, call an LLM (e.g., using Ollama) to analyze the DataFrame columns
    and sample data, and return a JSON mapping.
    
    For now, this function simply returns the default mapping.
    """
    # Here you would call your LLM service and parse its response.
    # For now, return the default mapping.
    return get_default_mapping(df)
