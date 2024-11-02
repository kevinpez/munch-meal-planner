import os
import requests
from flask import current_app
from werkzeug.utils import secure_filename
from datetime import datetime

class ImageHandler:
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    
    @staticmethod
    def save_image_from_url(url: str, recipe_name: str) -> str:
        """
        Downloads an image from a URL and saves it locally.
        Returns the local path to the saved image.
        """
        try:
            # Create images directory if it doesn't exist
            upload_folder = os.path.join(current_app.root_path, 'static', 'images', 'recipes')
            os.makedirs(upload_folder, exist_ok=True)
            
            # Generate unique filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = secure_filename(f"{recipe_name}_{timestamp}.jpg")
            
            # Download and save the image
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            filepath = os.path.join(upload_folder, filename)
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            # Return the relative path for database storage
            return f"images/recipes/{filename}"  # Consistent path format
            
        except Exception as e:
            current_app.logger.error(f"Error saving image: {str(e)}")
            return None