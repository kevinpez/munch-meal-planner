def get_meal_suggestion_prompt(preferences):
    return f"Based on the following dietary preferences, suggest a meal. Provide the response in JSON format including keys 'name', 'description', 'ingredients', and 'instructions'. Preferences: {preferences}"

def get_recipe_details_prompt(recipe_name):
    return f"Provide detailed recipe information for '{recipe_name}' in JSON format. Include 'ingredients' and 'instructions'." 