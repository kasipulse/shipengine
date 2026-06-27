import csv
import os
from sqlalchemy import create_engine, text, exc
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv("DB_URL")
if not db_url:
    raise ValueError("DB_URL not found.")

# Use pg8000 for pure-python connectivity
engine = create_engine(db_url.replace("postgresql://", "postgresql+pg8000://"))
DATA_DIR = 'data'

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
        conn.execute(text("DROP TABLE IF EXISTS compatibility, applications, vehicles, product_category, vehicle_type, seller, application_status CASCADE"))
        conn.commit()

        for file, table in files_to_import:
            path = os.path.join(DATA_DIR, file)
            if os.path.exists(path):
                print(f"--- Importing {file} ---")
                with open(path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        cols = ", ".join(row.keys())
                        vals = ", ".join([f":{k}" for k in row.keys()])
                        conn.execute(text(f"INSERT INTO {table} ({cols}) VALUES ({vals})"), row)
                conn.commit()
    print("Migration successful!")

if __name__ == "__main__":
    run_import()
