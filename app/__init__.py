# app/__init__.py
import os
from flask import Flask
from app.config import Config
from app.extensions import db, migrate, csrf, login, session
from app.utils.logger import setup_logger

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    login.init_app(app)
    session.init_app(app)

    # Setup logging
    setup_logger(app)

    # Register blueprints
    from app.routes import bp as main_bp
    from app.errors import errors as errors_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(errors_bp)

    # Add security headers
    from app.security import add_security_headers
    app.after_request(add_security_headers)

    return app

# Import User model after app creation to avoid circular imports
from app.models import User

@login.user_loader
def load_user(id):
    return User.query.get(int(id))
