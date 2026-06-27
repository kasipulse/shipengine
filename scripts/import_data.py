import csv
import os
from sqlalchemy import create_engine, text, exc
from dotenv import load_dotenv
from pathlib import Path

# 1. Setup paths
script_dir = Path(__file__).resolve().parent
dotenv_path = script_dir / '.env'
DATA_DIR = script_dir.parent / 'data'

# 2. Load environment variables
load_dotenv(dotenv_path=dotenv_path)
db_url = os.getenv("DB_URL")
if not db_url:
    raise ValueError(f"DB_URL not found! Please ensure .env exists at: {dotenv_path}")

# Use pg8000 for pure-python connectivity (no compilation needed)
engine = create_engine(db_url.replace("postgresql://", "postgresql+pg8000://"))

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
            path = DATA_DIR / file
            if path.exists():
                print(f"--- Importing {file} into {table} ---")
                with open(path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        row = {k: (None if v == "" else v) for k, v in row.items()}
                        cols = ", ".join(row.keys())
                        vals = ", ".join([f":{k}" for k in row.keys()])
                        conn.execute(text(f"INSERT INTO {table} ({cols}) VALUES ({vals})"), row)
                conn.commit()
            else:
                print(f"Warning: {path} not found.")

        # 3. Apply Foreign Key Constraints
        print("--- Applying Foreign Key Constraints ---")
        constraints = [
            "ALTER TABLE vehicles ADD CONSTRAINT fk_vehicle_type FOREIGN KEY (vehicle_type_id) REFERENCES vehicle_type(id)",
            "ALTER TABLE applications ADD CONSTRAINT fk_category FOREIGN KEY (category_id) REFERENCES product_category(id)",
            "ALTER TABLE applications ADD CONSTRAINT fk_seller FOREIGN KEY (seller_id) REFERENCES seller(id)",
            "ALTER TABLE compatibility ADD CONSTRAINT fk_app FOREIGN KEY (app_id) REFERENCES applications(app_id)",
            "ALTER TABLE compatibility ADD CONSTRAINT fk_vehicle FOREIGN KEY (vehicles_id) REFERENCES vehicles(id)"
        ]
        
        for sql in constraints:
            try:
                conn.execute(text(sql))
            except exc.SQLAlchemyError as e:
                print(f"Constraint error (check your CSV IDs): {e}")
        conn.commit()
                
    print("Migration successful! Your database is now fully relational.")

if __name__ == "__main__":
    run_import()
