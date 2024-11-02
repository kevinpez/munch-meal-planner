from flask_wtf import FlaskForm
from wtforms import TextAreaField
from wtforms.validators import DataRequired

class PreferencesForm(FlaskForm):
    preferences = TextAreaField('Dietary Preferences', validators=[DataRequired()])
