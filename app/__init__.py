# app/__init__.py
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import openai

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = 'your_secret_key'  # Replace with a secure key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///munch.db'

# Initialize extensions
db = SQLAlchemy(app)

# Set OpenAI API Key
openai.api_key = os.getenv('OPENAI_API_KEY')

from app import routes, models
