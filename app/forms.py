from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField, StringField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from app.models import User

class PreferencesForm(FlaskForm):
    preferences = TextAreaField('What are you in the mood for?', 
        validators=[
            DataRequired(message="Please tell us what you're craving"),
            Length(min=3, max=500, message="Your food preferences must be between 3 and 500 characters")
        ])
    submit = SubmitField('Generate Meal Plan')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', 
        validators=[
            DataRequired(),
            Length(min=3, max=64, message="Username must be between 3 and 64 characters")
        ])
    email = StringField('Email', 
        validators=[
            DataRequired(),
            Email(message="Please enter a valid email address"),
            Length(max=120)
        ])
    password = PasswordField('Password', 
        validators=[
            DataRequired(),
            Length(min=6, message="Password must be at least 6 characters long")
        ])
    password2 = PasswordField('Repeat Password', 
        validators=[
            DataRequired(), 
            EqualTo('password', message='Passwords must match')
        ])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')
