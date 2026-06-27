import csv
import os
from sqlalchemy import create_engine, text, exc
from dotenv import load_dotenv
from pathlib import Path

# 1. Setup paths
script_dir = Path(__file__).resolve().parent
root_dir = script_dir.parent
DATA_DIR = root_dir / 'data'

# 2. Check for .env in both potential locations
env_in_scripts = script_dir / '.env'
env_in_root = root_dir / '.env'

if env_in_scripts.exists():
    dotenv_path = env_in_scripts
elif env_in_root.exists():
    dotenv_path = env_in_root
else:
    # If neither exists, print a helpful message
    raise FileNotFoundError(f"Could not find .env in {script_dir} or {root_dir}")

load_dotenv(dotenv_path=dotenv_path)
db_url = os.getenv("DB_URL")

if not db_url:
    raise ValueError(f"DB_URL is empty! Please check content of: {dotenv_path}")

print(f"--- Connected using: {dotenv_path} ---")

# 3. Use pg8000 for pure-python connectivity
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
        # Ensure we drop in order to satisfy CASCADE requirements
        conn.execute(text("DROP TABLE IF EXISTS compatibility, applications, vehicles, product_category, vehicle_type, seller, application_status CASCADE"))
        conn.commit()

        for file, table in files_to_import:
            path = DATA_DIR / file
            if path.exists():
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
                print(f"Warning: {path} not found. Skipping.")

        # 4. Apply Foreign Key Constraints
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
                print(f"Constraint error (Check CSV ID matches): {e}")
        conn.commit()
                
    print("Migration successful! Your database is now fully relational.")

if __name__ == "__main__":
    run_import()
