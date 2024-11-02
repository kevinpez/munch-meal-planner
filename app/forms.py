from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length

class PreferencesForm(FlaskForm):
    preferences = TextAreaField('Dietary Preferences', 
        validators=[
            DataRequired(message="Please enter your dietary preferences"),
            Length(min=3, max=500, message="Preferences must be between 3 and 500 characters")
        ])
    submit = SubmitField('Generate Meal Plan')
