from flask import Blueprint, render_template, request, jsonify, current_app
from app.utils import get_user_profile, get_daily_intake, determine_next_meal, create_prompt

bp = Blueprint('main', __name__)

@bp.route('/', methods=['GET'])
def home():
    return render_template('index.html')

@bp.route('/get-meal-suggestion', methods=['POST'])
def get_meal_suggestion():
    try:
        data = request.json
        user_profile = {
            'dietary_restrictions': data.get('diet', 'none'),
            'allergies': [a.strip() for a in data.get('allergies', '').split(',') if a.strip()],
            'calorie_target': data.get('calories', 2000),
            'available_ingredients': [g.strip() for g in data.get('groceries', '').split(',') if g.strip()]
        }

        daily_intake = get_daily_intake()
        next_meal = determine_next_meal()

        # Create prompt and get response
        try:
            response = current_app.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": create_prompt(user_profile, daily_intake, next_meal)}
                ]
            )
            meal_plan = response.choices[0].message.content
        except Exception as e:
            current_app.logger.error(f"Error getting meal suggestion: {e}")
            raise

        # Generate an image using DALL-E
        try:
            image_prompt = f"A beautiful food photography style image of {meal_plan}"
            negative_prompt = "text, watermark, logo, blurry, distorted, low quality, cartoon style, illustration, anime, drawing"
            
            image_response = current_app.openai_client.images.generate(
                model="dall-e-3",
                prompt=f"{image_prompt}. Do not include: {negative_prompt}",
                size="1024x1024",
                quality="standard",
                n=1
            )
            image_url = image_response.data[0].url
            current_app.logger.info(f"Generated image URL: {image_url}")
        except Exception as e:
            current_app.logger.error(f"Error generating image: {e}")
            image_url = None

        return jsonify({
            'success': True,
            'meal_type': next_meal,
            'suggestion': meal_plan,
            'image_url': image_url
        })
    except Exception as e:
        current_app.logger.error(f"Error in get-meal-suggestion: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500 