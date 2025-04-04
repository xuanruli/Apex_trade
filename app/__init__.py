import os
from flask import Flask
from .api.routes import api_bp
from .db import initialize_database
from .services.auth import auth_bp

def create_app():
    app = Flask(__name__)

    database_path = os.path.join(os.path.dirname(__file__), 'db/apex_data.db')
    secret_key = os.getenv('SECRET_KEY', 'development_secret_key_test')

    app.register_blueprint(api_bp)
    app.register_blueprint(auth_bp)

    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

    app.config.from_mapping(
        SECRET_KEY=secret_key,
        DATABASE=database_path,
    )

    # initialize_database()

    return app


