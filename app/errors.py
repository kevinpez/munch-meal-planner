from flask import Blueprint, render_template
from werkzeug.exceptions import HTTPException

errors = Blueprint('errors', __name__)

@errors.app_errorhandler(404)
def not_found_error(error):
    return render_template('error.html', error="Page not found"), 404

@errors.app_errorhandler(500)
def internal_error(error):
    return render_template('error.html', error="An internal error occurred"), 500

@errors.app_errorhandler(Exception)
def handle_exception(error):
    if isinstance(error, HTTPException):
        return render_template('error.html', error=error.description), error.code
    return render_template('error.html', error="An unexpected error occurred"), 500 