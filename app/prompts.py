DIET_PROMPTS = {
    "vegetarian": """Create a vegetarian meal that excludes meat, fish, and seafood. 
    Focus on plant-based proteins like legumes, tofu, or tempeh. 
    Additional preferences: {preferences}""",
    
    "vegan": """Design a vegan meal that excludes all animal products including meat, dairy, eggs, and honey. 
    Emphasize whole plant foods and ensure complete protein sources. 
    Additional preferences: {preferences}""",
    
    "keto": """Develop a keto-friendly meal that is high in healthy fats (70-80%), moderate in protein (20-25%), 
    and very low in carbohydrates (5-10%). Keep net carbs under 20g. 
    Additional preferences: {preferences}""",
    
    "paleo": """Create a paleo-compliant meal focusing on whole foods that mirror the diet of hunter-gatherers. 
    Include lean meats, fish, fruits, vegetables, nuts, and seeds. Exclude grains, legumes, dairy, and processed foods. 
    Additional preferences: {preferences}""",
    
    "gluten-free": """Design a gluten-free meal that excludes wheat, barley, rye, and any derivatives. 
    Ensure no cross-contamination ingredients. Use naturally gluten-free whole foods. 
    Additional preferences: {preferences}""",
    
    "balanced": """Create a balanced meal following the plate method: 1/2 plate vegetables, 
    1/4 plate lean protein, 1/4 plate whole grains. Include healthy fats and ensure varied nutrients. 
    Additional preferences: {preferences}"""
}

def get_meal_suggestion_prompt(preferences, diet_types=None):
    """Generate a meal suggestion prompt based on diet types and preferences."""
    combined_prompt = ""
    if diet_types:
        diet_list = diet_types.split(',')
        for diet in diet_list:
            if diet in DIET_PROMPTS:
                combined_prompt += DIET_PROMPTS[diet].strip() + " AND "
        
        if combined_prompt:
            combined_prompt = combined_prompt[:-5]  # Remove trailing " AND "
            return f"{combined_prompt}. Additional preferences: {preferences}"
            
    return f"Based on the following dietary preferences, suggest a meal. Provide the response in JSON format including keys 'name', 'description', 'ingredients', and 'instructions'. Preferences: {preferences}"

def get_recipe_details_prompt(recipe_name):
    return f"Provide detailed recipe information for '{recipe_name}' in JSON format. Include 'ingredients' and 'instructions'."