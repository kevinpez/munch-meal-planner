def get_meal_suggestion_prompt(preferences):
    return [
        {
            "role": "system",
            "content": "You are a helpful chef that provides detailed recipe suggestions in JSON format."
        },
        {
            "role": "user", 
            "content": f"""Create a single detailed meal suggestion based on these preferences: {preferences}. 
Return the response in this exact JSON format:
{{
    "name": "Recipe Name",
    "description": "A brief description of the dish",
    "prep_time": "20 minutes",
    "cook_time": "30 minutes",
    "total_time": "50 minutes",
    "servings": 4,
    "calories": 400,
    "ingredients": [
        "1 cup ingredient one",
        "2 tbsp ingredient two"
    ],
    "instructions": [
        "Step 1: First instruction",
        "Step 2: Second instruction"
    ],
    "tips": [
        "Helpful tip one",
        "Helpful tip two"
    ],
    "benefits": [
        "Health benefit one",
        "Health benefit two"
    ],
    "dietary_info": [
        "Vegetarian",
        "Gluten-free"
    ]
}}"""
        }
    ]

def get_recipe_details_prompt(recipe_name):
    return [
        {
            "role": "system",
            "content": "You are a professional chef providing detailed recipes in JSON format."
        },
        {
            "role": "user", 
            "content": f"""Provide a detailed recipe for {recipe_name}. 
Return the response in this exact JSON format:
{{
    "name": "Recipe Name",
    "prep_time": "20 minutes",
    "cook_time": "30 minutes",
    "servings": 4,
    "ingredients": [
        "1 cup ingredient one",
        "2 tbsp ingredient two"
    ],
    "instructions": [
        "Step 1: First instruction",
        "Step 2: Second instruction"
    ],
    "tips": [
        "Helpful tip one",
        "Helpful tip two"
    ]
}}"""
        }
    ] 