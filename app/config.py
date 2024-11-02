import os
from dotenv import load_dotenv
import logging

load_dotenv()

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
)

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY') or 'dev-key-for-development-only'
    
    # Session configuration
    SESSION_TYPE = 'filesystem'
    
    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)
    elif not SQLALCHEMY_DATABASE_URI:
        SQLALCHEMY_DATABASE_URI = (
            'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'app.db')
        )
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # OpenAI configuration
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')