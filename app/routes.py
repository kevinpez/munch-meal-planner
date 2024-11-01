# app/routes.py
from flask import render_template, request, redirect, url_for, flash
from app import app, db
from app.models import Recipe
import openai
from app.prompts import get_meal_suggestion_prompt, get_recipe_details_prompt
import json

@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('home.html')

@app.route('/generate-meal-plan', methods=['POST'])
def generate_meal_plan():
    preferences = request.form.get('preferences')
    meal_data = get_single_meal(preferences)
    if meal_data:
        image_url = generate_image(meal_data['name'])
        return render_template('meal_plan.html', meal=meal_data, image_url=image_url)
    return render_template('meal_plan.html', error="Could not generate meal")

def get_single_meal(preferences):
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=get_meal_suggestion_prompt(preferences),
            max_tokens=500,
            temperature=0.7,
            response_format={ "type": "json_object" }
        )
        return json.loads(response.choices[0].message.content)
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
    try:
        recipe_name = request.form.get('recipe_name')
        if not recipe_name:
            flash('Recipe name is required', 'error')
            return redirect(url_for('home'))

        # Check if recipe already exists
        existing_recipe = Recipe.query.filter_by(name=recipe_name).first()
        if existing_recipe:
            flash('Recipe already saved', 'info')
            return redirect(url_for('cookbook'))

        recipe_details = get_recipe_details(recipe_name)
        if not recipe_details.get('ingredients') and not recipe_details.get('instructions'):
            flash('Could not fetch recipe details', 'error')
            return redirect(url_for('home'))

        new_recipe = Recipe(
            name=recipe_name,
            ingredients=recipe_details['ingredients'],
            instructions=recipe_details['instructions']
        )
        db.session.add(new_recipe)
        db.session.commit()
        flash('Recipe saved successfully!', 'success')
        return redirect(url_for('cookbook'))

    except Exception as e:
        db.session.rollback()
        flash(f'Error saving recipe: {str(e)}', 'error')
        return redirect(url_for('home'))

def get_recipe_details(recipe_name):
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=get_recipe_details_prompt(recipe_name),
            max_tokens=700,
            temperature=0.7,
            response_format={ "type": "json_object" }
        )
        recipe_data = json.loads(response.choices[0].message.content)
        return {
            'ingredients': '\n'.join(recipe_data['ingredients']),
            'instructions': '\n'.join(recipe_data['instructions'])
        }
    except Exception as e:
        print(f"Error fetching recipe details: {e}")
        return {'ingredients': '', 'instructions': ''}

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

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()  # Reset failed DB sessions
    return render_template('error.html', error=error), 500
