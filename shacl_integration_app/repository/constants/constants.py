import json
import os

json_file: str = os.getenv('FILES_JSON_PATH', 'files.json')

try:
    with open (json_file, 'r') as f:
        json_data: dict = json.loads(f.read())
        f.close()
except FileNotFoundError:
    json_data: dict = {}


# STATUS CODES

BAD_REQUEST: int = 400
OK: int = 200
INTERNAL_SERVER_ERROR: int = 500

__all__ = [*locals().keys()]