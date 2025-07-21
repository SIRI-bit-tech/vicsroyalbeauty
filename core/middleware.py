from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys
import re
from django.conf import settings
from django.core.cache import cache
from django.utils.deprecation import MiddlewareMixin
from bs4 import BeautifulSoup
import htmlmin

class PageSpeedMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        # Only process HTML responses
        if 'text/html' not in response.get('Content-Type', ''):
            return response
        
        # Don't process admin pages
        if request.path.startswith('/admin/'):
            return response
        
        # Get response content
        content = response.content.decode('utf-8')
        
        # Minify HTML
        content = htmlmin.minify(content,
            remove_comments=True,
            remove_empty_space=True,
            remove_all_empty_space=False,
            reduce_boolean_attributes=True
        )
        
        # Parse HTML
        soup = BeautifulSoup(content, 'html.parser')
        
        # Add lazy loading to images
        for img in soup.find_all('img'):
            if not img.get('loading'):
                img['loading'] = 'lazy'
        
        # Add preconnect for external resources
        head = soup.find('head')
        if head:
            preconnect_domains = {
                'https://fonts.googleapis.com',
                'https://fonts.gstatic.com',
                'https://cdn.tailwindcss.com',
                'https://cdnjs.cloudflare.com'
            }
            
            for domain in preconnect_domains:
                preconnect = soup.new_tag('link', rel='preconnect', href=domain)
                head.insert(0, preconnect)
        
        # Update response content
        response.content = str(soup).encode('utf-8')
        
        # Add security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        
        # Add cache headers for static content
        if 'static' in request.path or 'media' in request.path:
            response['Cache-Control'] = f'public, max-age={60 * 60 * 24 * 30}'  # 30 days
        
        return response

class ImageOptimizationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        if request.method == 'POST' and request.FILES:
            for field_name in request.FILES:
                image = request.FILES[field_name]
                if self._is_image(image):
                    optimized = self._optimize_image(image)
                    request.FILES[field_name] = optimized
        return None

    def _is_image(self, file):
        try:
            Image.open(file)
            file.seek(0)
            return True
        except:
            return False

    def _optimize_image(self, image):
        img = Image.open(image)
        
        # Convert to RGB if necessary
        if img.mode not in ('L', 'RGB', 'RGBA'):
            img = img.convert('RGB')
        
        # Calculate new dimensions while maintaining aspect ratio
        max_size = (800, 800)
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # Save with optimized settings
        output = BytesIO()
        
        # Preserve transparency for PNG
        if img.format == 'PNG':
            img.save(output, format='PNG', optimize=True)
        else:
            img.save(output, format='JPEG', quality=85, optimize=True)
        
        output.seek(0)
        
        return InMemoryUploadedFile(
            output,
            'ImageField',
            f"{image.name.split('.')[0]}.{'png' if img.format == 'PNG' else 'jpg'}",
            'image/png' if img.format == 'PNG' else 'image/jpeg',
            sys.getsizeof(output),
            None
        ) 