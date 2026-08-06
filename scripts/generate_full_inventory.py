import csv
import json
from pathlib import Path

# Setup file paths (pointing directly to the root project folder)
script_dir = Path(__file__).resolve().parent
PROJECT_ROOT = script_dir.parent

def build_full_inventory():
    applications_file = PROJECT_ROOT / 'applications.csv'
    
    if not applications_file.exists():
        print(f"Error: {applications_file} not found.")
        return

    print("--- Reading applications.csv and building inventory ---")
    inventory = []

    with open(applications_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row.get('price_usd') or not row.get('headline'):
                continue
                
            headline = row['headline'].strip()
            parts = headline.split(' ', 1)
            mfg = parts[0] if len(parts) > 0 else "Engine"
            mod = parts[1] if len(parts) > 1 else headline
            
            try:
                # Convert USD price to ZAR scale
                price_zar = str(int(float(row['price_usd'])) * 20)
            except ValueError:
                price_zar = "0"

            inventory.append({
                "manufacturer_name": mfg,
                "model_name": mod,
                "vehicle_type_id": row.get('vehicle_type_id', '1'),
                "price": price_zar,
                "image_url": "https://res.cloudinary.com/dwxgkbuln/image/upload/v1782581117/Toyota-Turbo-Engine_jmly6e.jpg"
            })

    output_json_path = PROJECT_ROOT / 'data' / 'engines.json'
    
    # Ensure data folder exists if it doesn't
    output_json_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_json_path, 'w', encoding='utf-8') as json_file:
        json.dump(inventory, json_file, indent=4)
        
    print(f"Successfully generated {output_json_path} containing {len(inventory)} items!")

if __name__ == "__main__":
    build_full_inventory()
