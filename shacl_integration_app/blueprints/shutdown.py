from flask import Blueprint, request, render_template
import os
import sys
sys.stdout.flush()

shutdown = Blueprint('shutdown', __name__)

@shutdown.route('/shutdown/<user>/<password>')
def shutdown_flask_app(user, password):
    if user == "sgonzage" and password == "Svger.gl.227":
        os._exit(0)
        return "Server shutting down..."
    else:
        return "Wrong credentials"
    
