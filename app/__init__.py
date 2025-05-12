import os
from flask import Flask
from .api.routes import api_bp
from .db import initialize_database
from .services.auth import auth_bp
from .models.logger import setup_logging
from flask_mail import Mail

mail = Mail()

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

    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME', 'smtp.gmail.com')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD', 'smtp.gmail.com')
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', 'smtp.gmail.com')

    mail.init_app(app)

    # initialize_database()

    setup_logging()
    return app


