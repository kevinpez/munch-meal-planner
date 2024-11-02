# app/models.py
from app import db
from sqlalchemy.orm import validates
from typing import Optional

class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    ingredients = db.Column(db.Text, nullable=True)
    instructions = db.Column(db.Text, nullable=True)

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

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'ingredients': self.ingredients,
            'instructions': self.instructions
        }

    def __repr__(self):
        return f'<Recipe {self.name}>'
