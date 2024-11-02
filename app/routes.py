# app/routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from app import db
from app.models import Recipe
from app.services.ai_service import AIService
from app.forms import PreferencesForm
from werkzeug.exceptions import BadRequest
from sqlalchemy.exc import SQLAlchemyError

bp = Blueprint('main', __name__)
ai_service = AIService()

@bp.route('/', methods=['GET', 'POST'])
def home():
    form = PreferencesForm()
    if form.validate_on_submit():
        preferences = form.preferences.data
        return redirect(url_for('main.generate_meal_plan', preferences=preferences))
    return render_template('home.html', form=form)

@bp.route('/generate-meal-plan', methods=['POST'])
def generate_meal_plan():
    try:
        preferences = request.form.get('preferences')
        diet_type = request.form.get('diet_type')
        
        if not preferences:
            raise BadRequest("Preferences are required")
        
        meal_data = ai_service.generate_meal_suggestion(preferences, diet_type)
        if not meal_data:
            flash('Could not generate meal suggestion. Please try again.', 'error')
            return redirect(url_for('main.home'))

        image_url = ai_service.generate_image(meal_data['name'])
        return render_template('meal_plan.html', meal=meal_data, image_url=image_url)

    except BadRequest as e:
        flash(str(e), 'error')
        return redirect(url_for('main.home'))
    except Exception as e:
        current_app.logger.error(f"Error in generate_meal_plan: {str(e)}")
        flash('An unexpected error occurred', 'error')
        return redirect(url_for('main.home'))

@bp.route('/save-recipe', methods=['POST'])
def save_recipe():
    try:
        recipe_name = request.form.get('recipe_name')
        if not recipe_name:
            raise BadRequest('Recipe name is required')

        # Check if recipe already exists
        existing_recipe = Recipe.query.filter_by(name=recipe_name).first()
        if existing_recipe:
            flash('Recipe already saved', 'info')
            return redirect(url_for('main.cookbook'))

        recipe_details = ai_service.get_recipe_details(recipe_name)
        if not recipe_details:
            flash('Could not fetch recipe details', 'error')
            return redirect(url_for('main.home'))

        # Convert lists to strings if necessary
        ingredients = recipe_details.get('ingredients', [])
        if isinstance(ingredients, list):
            ingredients = '\n'.join(ingredients)

        instructions = recipe_details.get('instructions', [])
        if isinstance(instructions, list):
            instructions = '\n'.join(instructions)

        new_recipe = Recipe(
            name=recipe_name,
            ingredients=ingredients,
            instructions=instructions
        )
        
        db.session.add(new_recipe)
        db.session.commit()
        flash('Recipe saved successfully!', 'success')
        return redirect(url_for('main.cookbook'))

    except BadRequest as e:
        flash(str(e), 'error')
        return redirect(url_for('main.home'))
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"Database error in save_recipe: {str(e)}")
        flash('Error saving recipe', 'error')
        return redirect(url_for('main.home'))
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Unexpected error in save_recipe: {str(e)}")
        flash('An unexpected error occurred', 'error')
        return redirect(url_for('main.home'))

@bp.route('/cookbook')
def cookbook():
    recipes = Recipe.query.all()
    return render_template('cookbook.html', recipes=recipes)

@bp.route('/grocery-list')
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

@bp.errorhandler(500)
def internal_error(error):
    db.session.rollback()  # Reset failed DB sessions
    return render_template('error.html', error=error), 500

@bp.route('/delete-recipe/<int:recipe_id>', methods=['POST'])
def delete_recipe(recipe_id):
    try:
        recipe = Recipe.query.get_or_404(recipe_id)
        db.session.delete(recipe)
        db.session.commit()
        flash('Recipe deleted successfully!', 'success')
        return redirect(url_for('main.cookbook'))
    except Exception as e:
        current_app.logger.error(f"Error deleting recipe: {str(e)}")
        flash('Error deleting recipe', 'error')
        return redirect(url_for('main.cookbook'))
