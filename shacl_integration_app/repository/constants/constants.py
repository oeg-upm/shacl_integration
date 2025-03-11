import json
import os

json_file: str = os.getenv('FILES_JSON_PATH', 'files.json')

try:
    with open (json_file, 'r') as f:
        json_data: dict = json.loads(f.read())
        f.close()
except FileNotFoundError:
    json_data: dict = {}