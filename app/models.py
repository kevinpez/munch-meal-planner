# app/models.py
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db, login
from sqlalchemy.orm import validates
from typing import Optional
from datetime import datetime
from flask import current_app

class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    ingredients = db.Column(db.Text, nullable=False)
    instructions = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(500))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, **kwargs):
        if not kwargs.get('name'):
            raise ValueError("Recipe name cannot be empty")
        super(Recipe, self).__init__(**kwargs)

    @validates('name')
    def validate_name(self, key, name):
        if not name or len(str(name).strip()) == 0:
            raise ValueError("Recipe name cannot be empty")
        if len(str(name)) > 100:
            raise ValueError("Recipe name must be less than 100 characters")
        return str(name).strip()

    @validates('ingredients', 'instructions')
    def validate_text_fields(self, key, value):
        if value is None:
            return value
        # Handle both string and list inputs
        if isinstance(value, list):
            return '\n'.join(str(item).strip() for item in value)
        return str(value).strip()

    @validates('image_url')
    def validate_image_url(self, key, url):
        if url:
            if not (url.startswith(('http://', 'https://')) or url.startswith('images/')):
                raise ValueError("Image URL must start with http://, https://, or images/")
            if len(url) > 500:
                raise ValueError("Image URL must be less than 500 characters")
        return url

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'ingredients': self.ingredients,
            'instructions': self.instructions,
            'image_url': self.image_url
        }

    def __repr__(self):
        return f'<Recipe {self.name}>'

    def get_base_ingredients(self):
        """Get list of base ingredients for shopping list."""
        try:
            from app.services.ai_service import AIService
            ai_service = AIService()
            recipe_details = ai_service.get_recipe_details(self.name)
            return recipe_details.get('base_ingredients', []) if recipe_details else []
        except Exception as e:
            current_app.logger.error(f"Error getting base ingredients: {str(e)}")
            return []

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    recipes = db.relationship('Recipe', backref='author', lazy='dynamic')

    @validates('username')
    def validate_username(self, key, username):
        if not username:
            raise ValueError("Username cannot be empty")
        if len(username) > 64:
            raise ValueError("Username must be less than 64 characters")
        return username.strip()

    @validates('email')
    def validate_email(self, key, email):
        if not email:
            raise ValueError("Email cannot be empty")
        if len(email) > 120:
            raise ValueError("Email must be less than 120 characters")
        return email.strip().lower()

    def set_password(self, password):
        if not password:
            raise ValueError("Password cannot be empty")
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

class GroceryItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    is_checked = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'is_checked': self.is_checked
        }

@login.user_loader
def load_user(id):
    return User.query.get(int(id))
