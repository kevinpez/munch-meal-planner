# app/__init__.py
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import openai
from dotenv import load_dotenv

load_dotenv()

if not os.getenv('OPENAI_API_KEY'):
    raise ValueError("OPENAI_API_KEY must be set in environment variables")

app = Flask(__name__, static_folder='static')

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default-dev-key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///munch.db'

# Initialize extensions
db = SQLAlchemy(app)

# Set OpenAI API Key
openai.api_key = os.getenv('OPENAI_API_KEY')

# Import models before creating tables
from app import models

# Create database tables
with app.app_context():
    db.create_all()

# Import routes after everything is initialized
from app import routes
