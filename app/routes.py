# app/routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from app import db
from app.models import Recipe, User
from app.services.ai_service import AIService
from app.forms import PreferencesForm, LoginForm, RegistrationForm
from werkzeug.exceptions import BadRequest
from sqlalchemy.exc import SQLAlchemyError
from flask_login import login_user, logout_user, login_required, current_user
import traceback

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
        diet_types = request.form.get('diet_type')  # Now contains comma-separated values
        
        if not preferences:
            raise BadRequest("Preferences are required")
        
        meal_data = ai_service.generate_meal_suggestion(preferences, diet_types)
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
@login_required
def save_recipe():
    try:
        recipe_name = request.form.get('recipe_name')
        if not recipe_name:
            raise BadRequest('Recipe name is required')

        # Check if recipe already exists for this user
        existing_recipe = Recipe.query.filter_by(
            name=recipe_name, 
            user_id=current_user.id
        ).first()
        
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
            instructions=instructions,
            user_id=current_user.id
        )
        
        db.session.add(new_recipe)
        db.session.commit()
        flash('Recipe saved successfully!', 'success')
        return redirect(url_for('main.cookbook'))

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error saving recipe: {str(e)}")
        flash('Error saving recipe', 'error')
        return redirect(url_for('main.home'))

@bp.route('/cookbook')
@login_required
def cookbook():
    recipes = Recipe.query.filter_by(user_id=current_user.id).all()
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

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'error')
            return redirect(url_for('main.login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('main.home'))
    return render_template('auth/login.html', title='Sign In', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.home'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    form = RegistrationForm()
    try:
        if form.validate_on_submit():
            current_app.logger.info(f'Starting registration process for username: {form.username.data}')
            
            user = User(username=form.username.data, email=form.email.data)
            user.set_password(form.password.data)
            current_app.logger.debug('User object created successfully')
            
            db.session.add(user)
            db.session.commit()
            
            current_app.logger.info(f'Successfully registered user: {user.username}')
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('main.login'))
            
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f'Database error: {str(e)}')
        current_app.logger.error(f'Traceback: {traceback.format_exc()}')
        flash(f'Database error: {str(e)}', 'error')
        return render_template('auth/register.html', title='Register', form=form)
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error during registration: {str(e)}')
        current_app.logger.error(f'Error type: {type(e).__name__}')
        current_app.logger.error(f'Traceback: {traceback.format_exc()}')
        flash(str(e), 'error')
        return render_template('auth/register.html', title='Register', form=form)
    
    return render_template('auth/register.html', title='Register', form=form)
