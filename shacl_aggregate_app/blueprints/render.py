from flask import Blueprint, request, render_template
import os
import sys
sys.stdout.flush()

render = Blueprint('render', __name__)

@render.route('/')
def home():
    return render_template('index.html')
    

