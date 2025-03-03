from flask import Flask
import sys
import secrets
from dotenv import load_dotenv
import os
sys.stdout.flush()


# Load .env
load_dotenv()

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_secret_key') #secrets.token_hex(16)

    from .blueprints.render import render as render_blueprint
    app.register_blueprint(render_blueprint)
    from .blueprints.aggregate import aggregate as aggregate_blueprint
    app.register_blueprint(aggregate_blueprint)
    from .blueprints.shutdown import shutdown as shutdown_blueprint
    app.register_blueprint(shutdown_blueprint)



    return app