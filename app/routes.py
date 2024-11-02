# app/routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify
from app import db
from app.models import Recipe, User, GroceryItem
from app.services.ai_service import AIService
from app.forms import PreferencesForm, LoginForm, RegistrationForm
from werkzeug.exceptions import BadRequest
from sqlalchemy.exc import SQLAlchemyError
from flask_login import login_user, logout_user, login_required, current_user
import traceback
from flask_wtf import FlaskForm
from app.utils.image_handler import ImageHandler
import os

bp = Blueprint('main', __name__)
ai_service = AIService()

@bp.route('/', methods=['GET', 'POST'])
def home():
    form = PreferencesForm()
    if form.validate_on_submit():
        preferences = form.preferences.data or "Suggest a balanced, healthy meal that's easy to prepare."
        return redirect(url_for('main.generate_meal_plan', preferences=preferences))
    return render_template('home.html', form=form)

@bp.route('/generate-meal-plan', methods=['GET', 'POST'])
@login_required
def generate_meal_plan():
    try:
        if request.method == 'POST':
            preferences = request.form.get('preferences', '')
            diet_type = request.form.get('diet_type', '')
            allergies = request.form.get('allergies', '')

            ai_service = AIService()
            meal_suggestion = ai_service.generate_meal_suggestion(
                preferences=preferences,
                diet_type=diet_type,
                allergies=allergies
            )

            if not meal_suggestion:
                flash('Failed to generate meal suggestion. Please try again.', 'error')
                return redirect(url_for('main.home'))

            # Generate image for the meal
            image_url = ai_service.generate_image(meal_suggestion['name'])
            if image_url:
                meal_suggestion['image_url'] = image_url
                current_app.logger.debug(f"Generated image URL: {image_url}")

            # Generate a new CSRF token for the save recipe form
            save_recipe_form = FlaskForm()
            return render_template('meal_plan.html', 
                                meal=meal_suggestion,
                                save_recipe_form=save_recipe_form)

        return render_template('home.html')

    except Exception as e:
        current_app.logger.error(f"Error in generate_meal_plan: {str(e)}")
        flash('An unexpected error occurred', 'error')
        return redirect(url_for('main.home'))

@bp.route('/save-recipe', methods=['POST'])
@login_required
def save_recipe():
    form = FlaskForm()
    if form.validate_on_submit():
        try:
            recipe_name = request.form.get('recipe_name')
            image_url = request.form.get('image_url')
            
            current_app.logger.debug(f"Received image URL: {image_url}")
            local_image_path = None
            
            if image_url:
                local_image_path = ImageHandler.save_image_from_url(image_url, recipe_name)
                current_app.logger.debug(f"Saved image locally at: {local_image_path}")
            
            recipe = Recipe(
                name=recipe_name,
                ingredients=request.form.get('ingredients'),
                instructions=request.form.get('instructions'),
                image_url=local_image_path,
                user_id=current_user.id
            )
            
            db.session.add(recipe)
            db.session.commit()
            
            # Automatically sync grocery list after saving recipe
            recipes = Recipe.query.filter_by(user_id=current_user.id).all()
            compile_ingredients(recipes)
            
            flash('Recipe saved successfully!', 'success')
            return redirect(url_for('main.cookbook'))
            
        except Exception as e:
            current_app.logger.error(f"Error saving recipe: {str(e)}")
            flash(str(e), 'error')
            return redirect(url_for('main.cookbook'))
    return redirect(url_for('main.cookbook'))

@bp.route('/cookbook')
@login_required
def cookbook():
    recipes = Recipe.query.filter_by(user_id=current_user.id).all()
    return render_template('cookbook.html', recipes=recipes)

@bp.route('/grocery-list')
@login_required
def grocery_list():
    grocery_items = GroceryItem.query.filter_by(user_id=current_user.id).all()
    return render_template('grocery_list.html', grocery_items=grocery_items)

@bp.route('/toggle-grocery-item', methods=['POST'])
@login_required
def toggle_grocery_item():
    data = request.get_json()
    item_id = data.get('item_id')
    is_checked = data.get('is_checked')
    
    item = GroceryItem.query.filter_by(id=item_id, user_id=current_user.id).first()
    if item:
        item.is_checked = is_checked
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'success': False}), 404

@bp.errorhandler(500)
def internal_error(error):
    db.session.rollback()  # Reset failed DB sessions
    return render_template('error.html', error=error), 500

@bp.route('/delete_recipe/<int:recipe_id>', methods=['POST'])
@login_required
def delete_recipe(recipe_id):
    try:
        recipe = Recipe.query.get_or_404(recipe_id)
        if recipe.user_id != current_user.id:
            flash('You cannot delete this recipe.', 'error')
            return redirect(url_for('main.cookbook'))
        
        # Delete the recipe
        db.session.delete(recipe)
        db.session.commit()
        
        # Sync grocery list with remaining recipes
        remaining_recipes = Recipe.query.filter_by(user_id=current_user.id).all()
        if compile_ingredients(remaining_recipes):
            flash('Recipe deleted and grocery list updated.', 'success')
        else:
            flash('Recipe deleted but error updating grocery list.', 'warning')
            
        return redirect(url_for('main.cookbook'))
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting recipe: {str(e)}")
        flash('Error deleting recipe.', 'error')
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

@bp.route('/add-grocery-item', methods=['POST'])
@login_required
def add_grocery_item():
    try:
        data = request.get_json()
        item_name = data.get('name')
        
        if not item_name:
            return jsonify({'success': False, 'error': 'Item name is required'}), 400
            
        new_item = GroceryItem(
            name=item_name.strip(),
            user_id=current_user.id
        )
        db.session.add(new_item)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'item': new_item.to_dict()
        })
        
    except Exception as e:
        current_app.logger.error(f"Error adding grocery item: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

def compile_ingredients(recipes):
    """Compile ingredients from recipes and sync with grocery list."""
    try:
        # Get all base ingredients from recipes
        base_ingredients = set()
        for recipe in recipes:
            if recipe.ingredients:
                # Get base ingredients from AI service
                recipe_details = ai_service.get_recipe_details(recipe.name)
                if recipe_details and 'base_ingredients' in recipe_details:
                    base_ingredients.update(recipe_details['base_ingredients'])
        
        if current_user.is_authenticated:
            # Get current user's grocery items
            current_items = GroceryItem.query.filter_by(user_id=current_user.id).all()
            current_item_names = {item.name.lower() for item in current_items}
            
            # Remove items that are no longer in any recipe
            for item in current_items:
                if item.name.lower() not in {ing.lower() for ing in base_ingredients}:
                    db.session.delete(item)
            
            # Add new items from recipes
            for ingredient in base_ingredients:
                if ingredient.lower() not in current_item_names:
                    new_item = GroceryItem(
                        name=ingredient,
                        user_id=current_user.id,
                        is_checked=False
                    )
                    db.session.add(new_item)
            
            db.session.commit()
            return True
            
    except Exception as e:
        current_app.logger.error(f"Error compiling ingredients: {str(e)}")
        db.session.rollback()
        return False

@bp.route('/sync-grocery-list', methods=['POST'])
@login_required
def sync_grocery_list():
    recipes = Recipe.query.filter_by(user_id=current_user.id).all()
    compile_ingredients(recipes)
    flash('Grocery list updated successfully!', 'success')
    return redirect(url_for('main.grocery_list'))
