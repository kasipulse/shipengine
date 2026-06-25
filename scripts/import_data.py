import pandas as pd
import os
import sqlalchemy
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load variables from .env
load_dotenv()

# Get the DB_URL
db_url = os.getenv("DB_URL")
if not db_url:
    raise ValueError("DB_URL not found in .env file. Please check your setup.")

engine = create_engine(db_url)

# Define your file mapping
files_to_import = {
    'vehicles.csv': 'vehicles',
    'product_category.csv': 'product_category',
    'vehicle_type.csv': 'vehicle_type',
    'applications.csv': 'applications',
    'compatibility.csv': 'compatibility',
    'seller.csv': 'seller',
    'application_status.csv': 'application_status'
}

def clean_database():
    """Drops all existing tables to ensure a clean slate for the import."""
    print("--- Cleaning database (dropping existing tables) ---")
    with engine.connect() as conn:
        # CASCADE ensures dependent tables (foreign keys) are dropped automatically
        conn.execute(text("DROP TABLE IF EXISTS compatibility CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS applications CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS vehicles CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS product_category CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS vehicle_type CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS seller CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS application_status CASCADE"))
        conn.commit()
    print("Database cleaned.")

def run_import():
    # 1. Clean the database first to avoid dependency errors
    clean_database()
    
    # 2. Import the files
    for file, table in files_to_import.items():
        if os.path.exists(file):
            print(f"--- Importing {file} into table '{table}' ---")
            df = pd.read_csv(file)
            
            # Using 'replace' now works because we manually handled the drop with CASCADE
            df.to_sql(table, engine, if_exists='replace', index=False)
            print(f"Success: '{table}' populated.")
        else:
            print(f"Warning: File {file} not found. Skipping.")

if __name__ == "__main__":
    run_import()
    print("All data migration tasks completed.")
