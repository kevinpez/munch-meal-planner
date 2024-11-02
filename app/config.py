import os
from datetime import timedelta

class Config:
    # Required configs with fallbacks for development
    SECRET_KEY = os.getenv('SECRET_KEY')
    if not SECRET_KEY:
        if os.getenv('FLASK_ENV') == 'development':
            SECRET_KEY = 'dev-key-for-development-only'
        else:
            raise ValueError("No SECRET_KEY set in environment variables")
    
    # Database config with proper URL handling
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)
    elif not SQLALCHEMY_DATABASE_URI:
        if os.getenv('FLASK_ENV') == 'development':
            SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'
        else:
            raise ValueError("No DATABASE_URL set in environment variables")
    
    # OpenAI config with development handling
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    if not OPENAI_API_KEY:
        if os.getenv('FLASK_ENV') == 'development':
            print("Warning: No OPENAI_API_KEY set. AI features will be disabled.")
        else:
            raise ValueError("No OPENAI_API_KEY set in environment variables")
    
    # Security Config
    SESSION_COOKIE_SECURE = True
    PERMANENT_SESSION_LIFETIME = timedelta(days=1)
    
    # API Config
    MAX_CONTENT_LENGTH = 1 * 1024 * 1024  # 1MB max request size 
    
    # Session Config
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    WTF_CSRF_TIME_LIMIT = 3600  # 1 hour
    WTF_CSRF_SSL_STRICT = True
    
    # Add these lines after the existing configurations
    SESSION_TYPE = 'filesystem'
    SESSION_FILE_DIR = os.path.join(os.getcwd(), 'flask_session')
    SESSION_FILE_THRESHOLD = 500  # Number of sessions stored in filesystem
    SESSION_PERMANENT = True
    PERMANENT_SESSION_LIFETIME = timedelta(days=1)