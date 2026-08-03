import csv
import json
from pathlib import Path

# Setup paths based on your repo structure
script_dir = Path(__file__).resolve().parent
DATA_DIR = script_dir.parent / 'data'

def generate_json_inventory():
    print("--- Reading CSV files from data directory ---")
    
    # Example: If your main engine inventory lives in 'vehicles.csv' or a combined file
    vehicles_file = DATA_DIR / 'vehicles.csv'
    
    if not vehicles_file.exists():
        print(f"Error: {vehicles_file} not found.")
        return

    engines_list = []

    with open(vehicles_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Clean up empty strings to None/empty
            cleaned_row = {k: (v if v != "" else None) for k, v in row.items()}
            engines_list.append(cleaned_row)

    # Output path for your website to read
    output_json_path = DATA_DIR / 'engines.json'
    
    with open(output_json_path, 'w', encoding='utf-8') as json_file:
        json.dump(engines_list, json_file, indent=4)
        
    print(f"Successfully generated {output_json_path} with {len(engines_list)} items!")

if __name__ == "__main__":
    generate_json_inventory()
