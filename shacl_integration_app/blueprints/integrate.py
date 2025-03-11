from flask import Blueprint, request, render_template
import os
import sys
import json
sys.stdout.flush()

integrate = Blueprint('integrate', __name__)


@integrate.route('/integrate', methods=['GET'])
def integration_possibilities():
    json_file: str = os.getenv('FILES_JSON_PATH', 'files.json')
    with open (json_file, 'r') as f:
        json_data: dict = json.loads(f.read())
        f.close()
    return json_data['1']



@integrate.route('/integrate/<id>/<operation>', methods=['POST'])
def integration(id, operation):
    # Join/AND
    # Disjoint/OR
    return f'Integration of shapes with {id}, using {operation} operation'