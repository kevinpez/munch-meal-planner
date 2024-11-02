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
        if not name or len(name.strip()) == 0:
            raise ValueError("Recipe name cannot be empty")
        if len(name) > 100:
            raise ValueError("Recipe name must be less than 100 characters")
        return name.strip()

    @validates('ingredients', 'instructions')
    def validate_text_fields(self, key, value):
        if value is not None:
            return value.strip()
        return value

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'ingredients': self.ingredients,
            'instructions': self.instructions
        }

    def __repr__(self):
        return f'<Recipe {self.name}>'
