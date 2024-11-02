import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("No SECRET_KEY set in environment variables")
    
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///app.db')
    if SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # OpenAI Config
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    if not OPENAI_API_KEY:
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