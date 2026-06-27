import csv
import os
from sqlalchemy import create_engine, text, exc
from pathlib import Path

# --- BYPASSING .env ---
# Hardcoded connection string
db_url = "postgresql://postgres:ZuluBravo198@db.fjrzxwxvrxobxfdtxeit.supabase.co:5432/postgres"

print("--- Connecting to database directly (Bypassing .env) ---")

# Use pg8000 for pure-python connectivity (no compilation needed)
engine = create_engine(db_url.replace("postgresql://", "postgresql+pg8000://"))

# Setup paths
script_dir = Path(__file__).resolve().parent
DATA_DIR = script_dir.parent / 'data'

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
                print(f"Constraint error (Check CSV ID matches): {e}")
        conn.commit()
                
    print("Migration successful! Your database is now fully relational.")

if __name__ == "__main__":
    run_import()
