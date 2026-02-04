"""
Cloudinary Integration for FarmAT
Provides image upload functionality for user profiles and livestock images
"""

import cloudinary
import cloudinary.uploader
from flask import current_app


def init_cloudinary():
    """Initialize Cloudinary with credentials from config."""
    cloudinary.config(
        cloud_name=current_app.config.get('CLOUDINARY_CLOUD_NAME'),
        api_key=current_app.config.get('CLOUDINARY_API_KEY'),
        api_secret=current_app.config.get('CLOUDINARY_API_SECRET')
    )


def upload_profile_image(file):
    """
    Upload a profile image to Cloudinary.
    
    Args:
        file: File object from Flask request.files
        
    Returns:
        str: Secure URL of the uploaded image, or None on failure
    """
    init_cloudinary()
    
    try:
        # Upload to Cloudinary with profile-specific folder
        result = cloudinary.uploader.upload(
            file,
            folder="farmat_profiles",
            transformation=[
                {'width': 400, 'height': 400, 'crop': 'fill', 'gravity': 'face'},
                {'quality': 'auto', 'fetch_format': 'auto'}
            ]
        )
        return result.get('secure_url')
    except Exception as e:
        current_app.logger.error(f"Cloudinary upload error: {e}")
        return None


def upload_livestock_image(file):
    """
    Upload a livestock image to Cloudinary.
    
    Args:
        file: File object from Flask request.files
        
    Returns:
        str: Secure URL of the uploaded image, or None on failure
    """
    init_cloudinary()
    
    try:
        # Upload to Cloudinary with inventory-specific folder
        result = cloudinary.uploader.upload(
            file,
            folder="farmat_inventory",
            transformation=[
                {'width': 800, 'height': 600, 'crop': 'fill'},
                {'quality': 'auto', 'fetch_format': 'auto'}
            ]
        )
        return result.get('secure_url')
    except Exception as e:
        current_app.logger.error(f"Cloudinary upload error: {e}")
        return None


def delete_image(public_id):
    """
    Delete an image from Cloudinary.
    
    Args:
        public_id: The public ID of the image to delete
        
    Returns:
        bool: True if deletion was successful, False otherwise
    """
    init_cloudinary()
    
    try:
        result = cloudinary.uploader.destroy(public_id)
        return result.get('result') == 'ok'
    except Exception as e:
        current_app.logger.error(f"Cloudinary delete error: {e}")
        return False
