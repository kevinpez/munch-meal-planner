from openai import OpenAI
from typing import Optional, Dict, Any
import json
from flask import current_app

client = OpenAI(api_key=current_app.config['OPENAI_API_KEY'])

class AIService:
    @staticmethod
    def validate_and_clean_input(text: str) -> str:
        """Sanitize user input"""
        return text.strip()[:500]  # Limit input length
    
    @staticmethod
    def generate_meal_suggestion(preferences: str) -> Optional[Dict[str, Any]]:
        """Generate meal suggestion with retry logic"""
        try:
            sanitized_preferences = AIService.validate_and_clean_input(preferences)
            
            # Updated system and user messages to enforce JSON structure
            system_message = """You are a meal planning assistant. Always respond with valid JSON containing these fields:
            {
                "name": "dish name",
                "description": "brief description",
                "prep_time": "preparation time",
                "cook_time": "cooking time",
                "total_time": "total time",
                "servings": "number of servings",
                "calories": "estimated calories per serving",
                "ingredients": ["list", "of", "ingredients"],
                "instructions": ["step 1", "step 2", "etc"]
            }"""
            
            user_message = f"Suggest a meal based on these preferences: {sanitized_preferences}. Respond only with JSON."
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=800,
                temperature=0.7,
                response_format={"type": "json_object"}  # Force JSON response
            )
            
            try:
                meal_data = json.loads(response.choices[0].message.content)
                required_fields = ['name', 'description', 'ingredients', 'instructions']
                if not all(field in meal_data for field in required_fields):
                    current_app.logger.error(f"Missing required fields in response: {meal_data}")
                    return None
                return meal_data
                
            except json.JSONDecodeError as e:
                current_app.logger.error(f"Failed to parse AI response as JSON: {response.choices[0].message.content}")
                return None
                
        except Exception as e:
            current_app.logger.error(f"Error generating meal suggestion: {str(e)}")
            return None
    
    @staticmethod
    def generate_image(meal_name: str) -> Optional[str]:
        """Generate an image for the meal using DALL-E"""
        try:
            response = client.images.generate(
                model="dall-e-3",
                prompt=f"A professional, appetizing photo of {meal_name}, food photography style, on a clean white plate",
                size="1024x1024",
                quality="standard",
                n=1,
            )
            
            # Return the URL of the generated image
            return response.data[0].url
        except Exception as e:
            current_app.logger.error(f"Error generating image: {str(e)}")
            return None