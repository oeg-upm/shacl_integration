from flask import Blueprint, request, render_template
import os
import sys
sys.stdout.flush()

shutdown = Blueprint('shutdown', __name__)

@shutdown.route('/shutdown/<user>/<password>')
def shutdown_flask_app(user, password):
    if user == "admin" and password == "admin":
        shutdown_server()
        return "Server shutting down..."
    else:
        return "Wrong credentials"


def shutdown_server():
    func = request.environ.get("werkzeug.server.shutdown")
    if func is None:
        raise RuntimeError("Not running with the Werkzeug Server")
    func()
