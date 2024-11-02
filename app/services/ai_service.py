from openai import OpenAI
from typing import Optional, Dict, Any
import json
from app import app

client = OpenAI(api_key=app.config['OPENAI_API_KEY'])

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
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that suggests meals based on user preferences."},
                    {"role": "user", "content": f"Based on these preferences, suggest a meal: {sanitized_preferences}"}
                ],
                max_tokens=500,
                temperature=0.7,
            )
            
            # Validate JSON response
            try:
                meal_data = json.loads(response.choices[0].message.content)
                required_fields = ['name', 'description', 'ingredients', 'instructions']
                if not all(field in meal_data for field in required_fields):
                    raise ValueError("Missing required fields in response")
                return meal_data
            except json.JSONDecodeError:
                app.logger.error("Failed to parse AI response as JSON")
                return None
                
        except Exception as e:
            app.logger.error(f"Error generating meal suggestion: {str(e)}")
            return None 