from openai import OpenAI
from typing import Optional, Dict, Any
import json
from flask import current_app

class AIService:
    def __init__(self):
        self.client = None
    
    def _ensure_client(self):
        if not self.client:
            self.client = OpenAI(api_key=current_app.config['OPENAI_API_KEY'])
        return self.client

    @staticmethod
    def validate_and_clean_input(text: str) -> str:
        return text.strip()[:500]

    def get_recipe_details(self, recipe_name: str) -> Optional[Dict[str, Any]]:
        try:
            client = self._ensure_client()
            sanitized_name = self.validate_and_clean_input(recipe_name)
            
            system_message = """You are a recipe details assistant. Respond with valid JSON containing:
            {
                "ingredients": "detailed list of ingredients with measurements",
                "instructions": "detailed cooking instructions"
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
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            current_app.logger.error(f"Error getting recipe details: {str(e)}")
            return None