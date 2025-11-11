import os
import random
import string
from agent.create_db.entities.table_info import TableOutput
import json
CSV_ROOT = './data/csv'
JSON_ROOT = './data/table_info'

def random_salt(length=8):
    letters = string.ascii_lowercase + string.digits
    return ''.join(random.choice(letters) for _ in range(length))

def choice_file_name(table_name: str, path_str: str) -> str:
    """Return a unique filename for a table by adding salt if duplicates exist."""
    # Ensure ROOT directory exists  
    os.makedirs(path_str, exist_ok=True)

    # List existing files in ROOT
    existing_files = set([i.split('.')[0] for i in os.listdir(path_str)])

    file_name = table_name

    # Add salt until it's unique
    while file_name in existing_files:
        salt = random_salt(6)
        file_name = f"{table_name}_{salt}"

    return file_name

def parse_and_save_csv(csv_content: str, table_name: str, save_dir=CSV_ROOT):
    if csv_content:
        # Pick a safe, non-duplicated filename
        file_path = save_dir
        name = choice_file_name(table_name,file_path)
        file_path = os.path.join(file_path, f"{name}.csv")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(csv_content)
        print(f"✅ CSV saved to {file_path}")
    else:
        print("⚠️ Could not extract CSV content from the output.")

    return name, file_path

def save_metadata(data: TableOutput, save_dir=JSON_ROOT):
    metadata_path = f"{save_dir}/{data.table_name}.json"
    data.csv_content = ""
    with open(metadata_path, 'w') as f:
        f.write(data.json())
    return metadata_path, TableOutput

def load_metadata(name: str,save_dir=JSON_ROOT):
    metadata_path = f"{save_dir}/{name}.json"
    with open(metadata_path, "r") as f:
        data_dict = json.load(f)
    table_obj = TableOutput(**data_dict)
    return table_obj