# app/routes.py
from flask import render_template, request, redirect, url_for
from app import app, db
from app.models import Recipe
import openai

@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('home.html')

@app.route('/generate-meal-plan', methods=['POST'])
def generate_meal_plan():
    preferences = request.form.get('preferences')
    meal = get_single_meal(preferences)
    if meal:
        image_url = generate_image(meal)
        return render_template('meal_plan.html', meal=meal, image_url=image_url)
    return render_template('meal_plan.html', error="Could not generate meal")

def get_single_meal(preferences):
    messages = [
        {"role": "user", "content": f"Create a single meal suggestion based on these preferences: {preferences}. Respond with just the meal name and a brief one-line description."}
    ]
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=100,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error generating meal: {e}")
        return None

def generate_image(meal_description):
    try:
        response = openai.images.generate(
            prompt=f"{meal_description}",
            n=1,
            size="256x256"
        )
        image_url = response.data[0].url
        return image_url
    except Exception as e:
        print(f"Error generating image: {e}")
        return None

@app.route('/save-recipe', methods=['POST'])
def save_recipe():
    recipe_name = request.form.get('recipe_name')
    recipe_details = get_recipe_details(recipe_name)
    new_recipe = Recipe(
        name=recipe_name,
        ingredients=recipe_details['ingredients'],
        instructions=recipe_details['instructions']
    )
    db.session.add(new_recipe)
    db.session.commit()
    return redirect(url_for('cookbook'))

def get_recipe_details(recipe_name):
    messages = [
        {"role": "user", "content": f"Provide a recipe for {recipe_name} with ingredients and step-by-step instructions."}
    ]
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=700,
            temperature=0.7,
        )
        recipe_text = response.choices[0].message.content.strip()
        ingredients, instructions = parse_recipe(recipe_text)
        return {'ingredients': ingredients, 'instructions': instructions}
    except Exception as e:
        print(f"Error fetching recipe details: {e}")
        return {'ingredients': '', 'instructions': ''}

def parse_recipe(recipe_text):
    try:
        ingredients_part, instructions_part = recipe_text.split('Instructions:')
        ingredients = ingredients_part.replace('Ingredients:', '').strip()
        instructions = instructions_part.strip()
    except ValueError:
        ingredients = ''
        instructions = recipe_text
    return ingredients, instructions

@app.route('/cookbook')
def cookbook():
    recipes = Recipe.query.all()
    return render_template('cookbook.html', recipes=recipes)

@app.route('/grocery-list')
def grocery_list():
    recipes = Recipe.query.all()
    ingredients_list = compile_ingredients(recipes)
    return render_template('grocery_list.html', ingredients=ingredients_list)

def compile_ingredients(recipes):
    ingredients = []
    for recipe in recipes:
        if recipe.ingredients:
            ingredients.extend([item.strip() for item in recipe.ingredients.split('\n') if item.strip()])
    unique_ingredients = list(set(ingredients))
    return unique_ingredients
