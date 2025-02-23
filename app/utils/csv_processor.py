# app/csv_importer.py
import pandas as pd
import json
import ollama  # Ensure the ollama package is installed and configured
from datetime import datetime


def detect_delimiter(file_path):
    """Detects delimiter by analyzing the first few lines of the file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        sample = f.read(1024)  # Read a small portion of the file
    delimiters = [',', ';', '\t', '|']
    return max(delimiters, key=lambda d: sample.count(d))

def generate_mapping_prompt(headers, sample_data):
    """Generates a highly strict prompt for AI-based column mapping, including a data sample."""
    return f'''
    You are an AI model tasked with mapping CSV column headers to a predefined schema.
    Your response **must be strictly** a JSON dictionary mapping the schema fields to the correct column names from the input data.
    
    The only acceptable format is:
    {{
        "date": "<original_column_name_1>",
        "amount": "<original_column_name_2>",
        "currency": "<original_column_name_3>",
        "description": "<original_column_name_4>",
        "recipient": "<original_column_name_5>"
    }}
    
    If no column from the input matches a given field, set its value to `null`.
    
    Instructions:
    - Your response **must** be a valid JSON dictionary and contain **only** the mappings.
    - **DO NOT** include any additional text, comments, explanations, or formatting issues.
    - The values in your response must be exact column names from the input headers or `null` if a match is not found.
    - Ensure that every key-value pair follows the expected schema strictly.
    
    Here is a small sample of the data for better understanding:
    {json.dumps(sample_data, indent=2, ensure_ascii=False)}
    
    Given these column headers: {headers}, provide only a JSON mapping in the exact format above.
    '''

def parse_csv(file_path, sample_size=5):
    """Loads CSV file with AI-assisted schema mapping, providing a sample of the data."""
    delimiter = detect_delimiter(file_path)
    df = pd.read_csv(file_path, delimiter=delimiter, dtype=str)
    
    # Select a small sample of data to provide context
    sample_data = df.sample(sample_size).to_dict(orient='records')
    
    prompt = generate_mapping_prompt(list(df.columns), sample_data)
    result = ollama.generate(model="llama3:8b", prompt=prompt)
    
    try:
        column_mapping = json.loads(result.get('response'))  # Ensure we only get pure JSON
        print(column_mapping)
    except json.JSONDecodeError:
        raise ValueError("AI response could not be parsed as JSON")
    
    # Create a new transactions DataFrame using the mapping
    transactions_data = []
    for _, row in df.iterrows():
        transaction = {
            "date": row[column_mapping["date"]] if column_mapping["date"] else datetime.now(),
            "amount": float(row[column_mapping["amount"]]) if column_mapping["amount"] else 0,
            "currency": row[column_mapping["currency"]] if column_mapping["currency"] else "CHF",
            "description": row[column_mapping["description"]] if column_mapping["description"] else "",
            "recipient": row[column_mapping["recipient"]] if column_mapping["recipient"] else "None",
            "raw_data": json.dumps(row.to_dict(), ensure_ascii=False)
        }
        transactions_data.append(transaction)

    transactions_df = pd.DataFrame(transactions_data)
    transactions_df['date'] = pd.to_datetime(transactions_df['date'], errors='coerce')

    # Return the DataFrame for further processing, e.g., converting rows to TransactionBase instances
    return transactions_df
