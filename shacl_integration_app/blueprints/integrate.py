from flask import Blueprint, request, render_template
import os
import sys
import json
from shacl_integration_app.repository.constants import *
sys.stdout.flush()

integrate = Blueprint('integrate', __name__)


@integrate.route('/integration_options', methods=['GET'])
def integration_possibilities() -> dict:
    json_response: dict = {key: json_data[key]['description'] for key in json_data.keys()}
    return json_response


@integrate.route('/integrate/<id>/<operation>', methods=['POST'])
def integration(id: str, operation: str) -> str:
    # Join/AND
    # Disjoint/OR
    if operation not in ['union', 'intersection']:
        return 'Invalid operation, please use either \"union\" or \"intersection\"'
    elif id not in json_data.keys():
        return f'Invalid id, please use one of the following: {", ".join([f"[{str(key)}]" for key in json_data.keys()])}'
    
    return f'Integration of shapes with id: [{id}], using operation: [{operation}]'