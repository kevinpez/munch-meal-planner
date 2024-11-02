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

ALLERGY_PROMPTS = {
    "nuts": "Strictly avoid all tree nuts including almonds, walnuts, pecans, cashews, etc.",
    "peanuts": "Strictly avoid peanuts and peanut-derived ingredients.",
    "dairy": "Exclude all dairy products including milk, cheese, yogurt, and butter.",
    "eggs": "Exclude all eggs and egg-derived ingredients.",
    "shellfish": "Avoid all shellfish including shrimp, crab, lobster, and mollusks.",
    "soy": "Exclude all soy products and soy-derived ingredients."
}

def get_meal_suggestion_prompt(preferences, diet_types=None, allergies=None):
    """Generate a meal suggestion prompt based on diet types, allergies, and preferences."""
    combined_prompt = []
    
    if diet_types:
        diet_list = diet_types.split(',')
        for diet in diet_list:
            if diet in DIET_PROMPTS:
                combined_prompt.append(DIET_PROMPTS[diet].strip())
    
    if allergies:
        allergy_list = allergies.split(',')
        for allergy in allergy_list:
            if allergy in ALLERGY_PROMPTS:
                combined_prompt.append(ALLERGY_PROMPTS[allergy])
    
    if combined_prompt:
        prompt = " AND ".join(combined_prompt)
        return f"{prompt}. Additional preferences: {preferences}"
        
    return f"Based on the following dietary preferences, suggest a meal. {preferences}"

def get_recipe_details_prompt(recipe_name):
    return {
        "system": """You are a recipe details assistant. Provide recipe information in the following JSON format:
        {
            "ingredients": [
                {"item": "2 cups flour", "base_item": "flour"},
                {"item": "1 cup milk", "base_item": "milk"}
            ],
            "instructions": ["step 1", "step 2"]
        }
        Always break down ingredients into their base items for shopping list purposes.""",
        "user": f"Provide detailed recipe information for '{recipe_name}'"
    }