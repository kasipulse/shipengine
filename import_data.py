import pandas as pd
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load variables from .env
load_dotenv()

# Get the DB_URL
db_url = os.getenv("DB_URL")
if not db_url:
    raise ValueError("DB_URL not found in .env file.")

engine = create_engine(db_url)

# Updated to look in the /data folder as discussed
DATA_DIR = 'data'

files_to_import = {
    'vehicle_type.csv': 'vehicle_type',
    'product_category.csv': 'product_category',
    'application_status.csv': 'application_status',
    'seller.csv': 'seller',
    'vehicles.csv': 'vehicles',
    'applications.csv': 'applications',
    'compatibility.csv': 'compatibility'
}

def clean_database():
    print("--- Cleaning database (dropping existing tables) ---")
    with engine.connect() as conn:
        # Order matters for CASCADE: child tables first
        conn.execute(text("DROP TABLE IF EXISTS compatibility, applications, vehicles, product_category, vehicle_type, seller, application_status CASCADE"))
        conn.commit()
    print("Database cleaned.")

def run_import():
    clean_database()
    
    # 1. Import base tables first (Parents)
    # 2. Import dependent tables last (Children)
    for file, table in files_to_import.items():
        file_path = os.path.join(DATA_DIR, file)
        
        if os.path.exists(file_path):
            print(f"--- Importing {file} into table '{table}' ---")
            df = pd.read_csv(file_path)
            
            # Use 'replace' to create tables with correct inferred types
            df.to_sql(table, engine, if_exists='replace', index=False)
            print(f"Success: '{table}' populated.")
        else:
            print(f"Warning: File {file_path} not found. Skipping.")

    # Apply constraints after data is loaded
    add_constraints()

def add_constraints():
    print("--- Applying Foreign Key Constraints ---")
    with engine.connect() as conn:
        queries = [
            "ALTER TABLE vehicles ADD CONSTRAINT fk_vehicle_type FOREIGN KEY (vehicle_type_id) REFERENCES vehicle_type(id)",
            "ALTER TABLE applications ADD CONSTRAINT fk_category FOREIGN KEY (category_id) REFERENCES product_category(id)",
            "ALTER TABLE applications ADD CONSTRAINT fk_seller FOREIGN KEY (seller_id) REFERENCES seller(id)",
            "ALTER TABLE compatibility ADD CONSTRAINT fk_app FOREIGN KEY (app_id) REFERENCES applications(app_id)",
            "ALTER TABLE compatibility ADD CONSTRAINT fk_vehicle FOREIGN KEY (vehicles_id) REFERENCES vehicles(id)"
        ]
        for q in queries:
            conn.execute(text(q))
        conn.commit()
    print("Constraints applied successfully.")

if __name__ == "__main__":
    run_import()
    print("All data migration tasks completed.")
