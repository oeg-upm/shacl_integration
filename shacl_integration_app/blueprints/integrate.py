from flask import Blueprint, request, render_template
import os
import sys
sys.stdout.flush()

integrate = Blueprint('integrate', __name__)

@integrate.route('/integrate')
def aggregation():
    # Join/AND
    # Disjoint/OR
    return "Aggregating shacl shapes..."
    

