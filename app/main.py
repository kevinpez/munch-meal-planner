from datetime import datetime
from typing import Dict
from openai import OpenAI

def get_user_profile() -> Dict[str, any]:
    return {
        'name': 'John Doe',
        'age': 30,
        'gender': 'male',
        'dietary_preferences': 'vegetarian',
        'allergies': 'none',
        'caloric_goal': 2000
    }

def get_daily_intake() -> Dict[str, str]:
    return {
        'breakfast': 'oatmeal with fruits',
        'lunch': 'quinoa salad',
        'snacks': 'nuts and yogurt'
    }

def determine_next_meal() -> str:
    current_hour = datetime.now().hour
    if current_hour < 10:
        return 'breakfast'
    elif current_hour < 14:
        return 'lunch'
    elif current_hour < 18:
        return 'snack'
    else:
        return 'dinner'

def create_prompt(user_profile: Dict[str, any], daily_intake: Dict[str, str], next_meal: str) -> str:
    available_ingredients = user_profile.get('available_ingredients', [])
    ingredients_text = ', '.join(available_ingredients) if available_ingredients else 'None specified'
    
    return (
        f"User Profile:\n"
        f"Dietary Restrictions: {user_profile.get('dietary_restrictions', 'None')}\n"
        f"Allergies: {', '.join(user_profile.get('allergies', [])) or 'None'}\n"
        f"Caloric Target: {user_profile.get('calorie_target', 2000)} kcal\n"
        f"Available Ingredients: {ingredients_text}\n\n"
        f"Today's Intake:\n"
        f"Breakfast: {daily_intake.get('breakfast', 'None')}\n"
        f"Lunch: {daily_intake.get('lunch', 'None')}\n"
        f"Snacks: {daily_intake.get('snacks', 'None')}\n\n"
        f"Please suggest a {next_meal} plan that preferably uses the available ingredients. "
        f"If additional ingredients are needed, please note them separately. "
        f"Return your response as a JSON object with the following structure:\n"
        "{\n"
        '  "name": "meal name",\n'
        '  "description": "brief description",\n'
        '  "ingredients": ["ingredient 1 with measurement", "ingredient 2 with measurement"],\n'
        '  "additional_needed": ["additional ingredient 1", "additional ingredient 2"],\n'
        '  "instructions": ["step 1", "step 2"],\n'
        '  "calories": "approximate calories"\n'
        "}"
    )

def get_meal_suggestion(prompt: str) -> str:
    client = OpenAI()  # This will automatically use your OPENAI_API_KEY from environment
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  # or your preferred model
        messages=[
            {"role": "system", "content": "You are a helpful meal planning assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    
    return response.choices[0].message.content
