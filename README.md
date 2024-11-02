# Munch Meal Planner

Munch is a personalized meal planning application that uses OpenAI's GPT model to suggest meal plans based on user dietary preferences and current intake.

## Features

### User Management
- User registration and authentication system
- Secure password hashing and validation
- Session management for logged-in users

### Meal Planning
- AI-powered meal suggestions based on dietary preferences
- Support for multiple diet types:
  - Vegetarian
  - Vegan
  - Keto
  - Paleo
  - Gluten-Free
  - Balanced
- Detailed recipe information including:
  - Ingredients list
  - Step-by-step instructions
  - Preparation and cooking times
  - Serving sizes
  - Caloric information
  - Health benefits
  - Dietary tags

### Recipe Management
- Personal cookbook for storing favorite recipes
- DALL·E image generation for recipe visualization
- Ability to save and delete recipes
- Organized recipe display with ingredients and instructions

### Additional Features
- Responsive design for mobile and desktop
- Smart grocery list generation based on saved recipes
- Security features including CSRF protection and secure headers
- Error handling and user feedback system

## Technical Requirements

### Prerequisites
- Python 3.11.7 or higher
- PostgreSQL database (optional, SQLite supported by default)
- OpenAI API key for:
  - GPT model integration
  - DALL·E image generation

### Dependencies
- Flask 3.0.0+
- SQLAlchemy for database management
- Flask-Login for user authentication
- WTForms for form handling
- Email-validator for user registration
- Additional requirements listed in requirements.txt

## Setup Instructions

1. Clone the repository
2. Create and activate a virtual environment:
   ```bash
   pip install -r requirements.txt

## Database Setup
