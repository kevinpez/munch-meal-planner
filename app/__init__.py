# app/__init__.py
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from logging.config import dictConfig
from app.config import Config
from flask_session import Session
from flask_login import LoginManager

# Create db instance before importing models
db = SQLAlchemy()

# Import User model after db initialization
from app.models import User

# Configure logging
dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})

# Initialize extensions
migrate = Migrate()
csrf = CSRFProtect()
session = Session()
login = LoginManager()
login.login_view = 'main.login'
login.login_message_category = 'info'

# Add after the extensions initialization
if not os.path.exists('flask_session'):
    os.makedirs('flask_session')

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    session.init_app(app)
    login.init_app(app)

    # Add security headers
    from app.security import add_security_headers
    app.after_request(add_security_headers)

    with app.app_context():
        # Import routes here to avoid circular imports
        from app.routes import bp
        from app.errors import errors
        app.register_blueprint(bp)
        app.register_blueprint(errors)
        
        # Create tables
        db.create_all()

    return app

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

# Create the app instance
app = create_app()
