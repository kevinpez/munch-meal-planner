from openai import OpenAI
from typing import Optional, Dict, Any
import json
from flask import current_app
from app.prompts import get_meal_suggestion_prompt

class AIService:
    def __init__(self):
        self.client = None
    
    def _ensure_client(self):
        if not self.client:
            self.client = OpenAI(api_key=current_app.config['OPENAI_API_KEY'])
        return self.client

    def generate_meal_suggestion(self, preferences: str, diet_type: Optional[str] = None, allergies: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Generate a meal suggestion based on user preferences, diet type, and allergies."""
        try:
            client = self._ensure_client()
            sanitized_preferences = self.validate_and_clean_input(preferences)
            
            system_message = """You are a meal planning assistant. Respond with valid JSON containing:
            {
                "name": "recipe name",
                "description": "brief description",
                "ingredients": ["list", "of", "ingredients"],
                "instructions": ["step 1", "step 2", "etc"],
                "prep_time": "preparation time",
                "cook_time": "cooking time",
                "total_time": "total time",
                "servings": "number of servings",
                "calories": "estimated calories",
                "tips": ["cooking tip 1", "cooking tip 2"],
                "benefits": ["health benefit 1", "health benefit 2"],
                "dietary_info": ["vegetarian", "gluten-free", etc],
                "image_url": "https://example.com/image.jpg (use a real, relevant food image URL)"
            }"""
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": get_meal_suggestion_prompt(sanitized_preferences, diet_type, allergies)}
                ],
                temperature=0.7,
                max_tokens=800,
                response_format={"type": "json_object"}
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            current_app.logger.error(f"Error generating meal suggestion: {str(e)}")
            return None

    @staticmethod
    def validate_and_clean_input(text: str) -> str:
        """Validate and clean user input."""
        return text.strip()[:500]

    def generate_image(self, meal_name: str) -> Optional[str]:
        """Generate an image for the meal using DALL-E."""
        try:
            client = self._ensure_client()
            sanitized_name = self.validate_and_clean_input(meal_name)
            
            response = client.images.generate(
                model="dall-e-3",
                prompt=f"A professional food photography style image of {sanitized_name}, on a beautiful plate with garnish, overhead view",
                size="1024x1024",
                quality="standard",
                n=1,
            )
            
            return response.data[0].url
            
        except Exception as e:
            current_app.logger.error(f"Error generating image: {str(e)}")
            return None

    def get_recipe_details(self, recipe_name: str) -> Optional[Dict[str, Any]]:
        try:
            client = self._ensure_client()
            sanitized_name = self.validate_and_clean_input(recipe_name)
            
            system_message = """You are a recipe details assistant. Respond with valid JSON containing:
            {
                "ingredients": ["ingredient 1", "ingredient 2", ...],
                "instructions": ["step 1", "step 2", ...]
            }"""
            
            user_message = f"Provide detailed recipe information for '{sanitized_name}'"
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=800,
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Ensure we have lists for both ingredients and instructions
            if isinstance(result.get('ingredients'), str):
                result['ingredients'] = [result['ingredients']]
            if isinstance(result.get('instructions'), str):
                result['instructions'] = [result['instructions']]
                
            return result
            
        except Exception as e:
            current_app.logger.error(f"Error getting recipe details: {str(e)}")
            return None