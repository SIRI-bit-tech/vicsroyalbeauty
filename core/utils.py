from cloudinary import CloudinaryImage
from django.conf import settings

def get_optimized_image_url(image_field, transformation_type='auto'):
    """
    Get optimized image URL with Cloudinary transformations
    
    Args:
        image_field: CloudinaryField instance
        transformation_type: 'thumbnail', 'medium', 'large', or 'auto'
    
    Returns:
        Optimized image URL or None if no image
    """
    if not image_field:
        return None
    
    transformations = {
        'thumbnail': [
            {'width': 150, 'height': 150, 'crop': 'fill', 'quality': 'auto'},
            {'fetch_format': 'auto'}
        ],
        'medium': [
            {'width': 400, 'height': 400, 'crop': 'fill', 'quality': 'auto'},
            {'fetch_format': 'auto'}
        ],
        'large': [
            {'width': 800, 'height': 800, 'crop': 'fill', 'quality': 'auto'},
            {'fetch_format': 'auto'}
        ],
        'auto': [
            {'quality': 'auto', 'fetch_format': 'auto'}
        ]
    }
    
    try:
        return CloudinaryImage(str(image_field)).build_url(
            transformation=transformations.get(transformation_type, transformations['auto'])
        )
    except Exception:
        # Fallback to original URL if transformation fails
        return str(image_field) if image_field else None

def get_profile_image_url(image_field):
    """Get optimized profile image URL with face detection"""
    if not image_field:
        return None
    
    try:
        return CloudinaryImage(str(image_field)).build_url(
            transformation=[
                {'width': 200, 'height': 200, 'crop': 'fill', 'gravity': 'face', 'quality': 'auto'},
                {'fetch_format': 'auto'}
            ]
        )
    except Exception:
        return str(image_field) if image_field else None

def get_category_image_url(image_field):
    """Get optimized category image URL"""
    if not image_field:
        return None
    
    try:
        return CloudinaryImage(str(image_field)).build_url(
            transformation=[
                {'width': 400, 'height': 300, 'crop': 'fill', 'quality': 'auto'},
                {'fetch_format': 'auto'}
            ]
        )
    except Exception:
        return str(image_field) if image_field else None 