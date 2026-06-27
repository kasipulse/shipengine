import csv
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from pathlib import Path

# 1. Setup path to .env file (assuming it's in the same folder as this script)
script_dir = Path(__file__).resolve().parent
dotenv_path = script_dir / '.env'

# 2. Load environment variables
load_dotenv(dotenv_path=dotenv_path)

db_url = os.getenv("DB_URL")
if not db_url:
    raise ValueError(f"DB_URL not found! Expected at: {dotenv_path}")

print(f"Connecting to database using: {dotenv_path}")

# 3. Use pg8000 for pure-python connectivity
engine = create_engine(db_url.replace("postgresql://", "postgresql+pg8000://"))

# Define folder path relative to the script's parent directory
DATA_DIR = script_dir.parent / 'data'

# Files in dependency order
files_to_import = [
    ('vehicle_type.csv', 'vehicle_type'),
    ('product_category.csv', 'product_category'),
    ('application_status.csv', 'application_status'),
    ('seller.csv', 'seller'),
    ('vehicles.csv', 'vehicles'),
    ('applications.csv', 'applications'),
    ('compatibility.csv', 'compatibility')
]

def run_import():
    with engine.connect() as conn:
        print("--- Cleaning database ---")
        # Ensure we drop in order to satisfy CASCADE requirements
        conn.execute(text("DROP TABLE IF EXISTS compatibility, applications, vehicles, product_category, vehicle_type, seller, application_status CASCADE"))
        conn.commit()

        for file, table in files_to_import:
            path = DATA_DIR / file
            if os.path.exists(path):
                print(f"--- Importing {file} into {table} ---")
                with open(path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        # Clean up row: remove empty strings/keys
                        row = {k: (None if v == "" else v) for k, v in row.items()}
                        cols = ", ".join(row.keys())
                        vals = ", ".join([f":{k}" for k in row.keys()])
                        conn.execute(text(f"INSERT INTO {table} ({cols}) VALUES ({vals})"), row)
                conn.commit()
            else:
                print(f"Warning: {path} not found.")
                
    print("Migration successful!")

if __name__ == "__main__":
    run_import()
