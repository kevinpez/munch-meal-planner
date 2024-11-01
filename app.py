from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import openai
import os
from main import get_user_profile, get_daily_intake, determine_next_meal, create_prompt
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')

if not api_key:
    raise ValueError("No API key found in environment variables")

# Initialize OpenAI client
client = openai.OpenAI(api_key=api_key)

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///munch.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key')  # Required for Flask-Login

# Initialize database
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Update the port configuration
port = int(os.getenv('PORT', 5000))

@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

@app.route('/get-meal-suggestion', methods=['POST'])
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
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": create_prompt(user_profile, daily_intake, next_meal)}
                ]
            )
            meal_plan = response.choices[0].message.content
        except Exception as e:
            app.logger.error(f"Error getting meal suggestion: {e}")
            raise

        # Generate an image using DALL-E
        try:
            image_prompt = f"A beautiful food photography style image of {meal_plan}"
            negative_prompt = "text, watermark, logo, blurry, distorted, low quality, cartoon style, illustration, anime, drawing"
            
            image_response = client.images.generate(
                model="dall-e-3",
                prompt=f"{image_prompt}. Do not include: {negative_prompt}",
                size="1024x1024",
                quality="standard",
                n=1
            )
            image_url = image_response.data[0].url
            app.logger.info(f"Generated image URL: {image_url}")
        except Exception as e:
            app.logger.error(f"Error generating image: {e}")
            # If image generation fails, continue without an image
            image_url = None

        return jsonify({
            'success': True,
            'meal_type': next_meal,
            'suggestion': meal_plan,
            'image_url': image_url
        })
    except Exception as e:
        app.logger.error(f"Error in get-meal-suggestion: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    # Use production config when deploying
    app.run(host='0.0.0.0', port=port)
