from flask import Blueprint, request, render_template
import os
import sys
sys.stdout.flush()

aggregate = Blueprint('aggregate', __name__)

@aggregate.route('/aggregate')
def aggregation():
    return "Aggregating shacl shapes..."
    

