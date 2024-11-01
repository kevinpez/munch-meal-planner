# run.py
from app import app, db
import os

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
