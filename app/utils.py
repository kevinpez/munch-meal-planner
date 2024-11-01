from datetime import datetime
from typing import Dict, Any

def get_user_profile() -> Dict[str, Any]:
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
        'snacks': 'nuts and yogurt',
        'dinner': 'vegetable stir-fry'
    }

def determine_next_meal() -> str:
    MEAL_TIMES = {
        'breakfast': 10,
        'lunch': 14,
        'snack': 18
    }
    
    current_hour = datetime.now().hour
    for meal, threshold in MEAL_TIMES.items():
        if current_hour < threshold:
            return meal
    return 'dinner'

def create_prompt(user_profile: Dict[str, Any], daily_intake: Dict[str, str], next_meal: str) -> str:
    prompt = f"Given that I am a {user_profile['age']} year old {user_profile['gender']}, "
    prompt += f"following a {user_profile['dietary_preferences']} diet with {user_profile['caloric_goal']} calorie goal, "
    prompt += f"and having allergies: {user_profile['allergies']}, "
    prompt += f"and having eaten {', '.join(daily_intake.values())} today, "
    prompt += f"what would you recommend for {next_meal}?"
    return prompt