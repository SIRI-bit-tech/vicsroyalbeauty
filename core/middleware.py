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
import time
from django.http import HttpResponse, JsonResponse

class RateLimitMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Get client IP
        client_ip = self.get_client_ip(request)
        
        # Define rate limits only for sensitive endpoints
        rate_limits = {
            'api': {'requests': 1000, 'window': 3600},     # 1000 API requests per hour
            'login': {'requests': 5, 'window': 300},       # 5 login attempts per 5 minutes
            'contact': {'requests': 10, 'window': 3600},   # 10 contact form submissions per hour
        }
        
        # Only apply rate limiting to sensitive endpoints
        path = request.path
        limit_type = None
        
        if path.startswith('/api/'):
            limit_type = 'api'
        elif path.startswith('/accounts/login'):
            limit_type = 'login'
        elif path.startswith('/contact'):
            limit_type = 'contact'
            
        # If not a sensitive endpoint, allow the request
        if not limit_type:
            return None
            
        limit = rate_limits[limit_type]
        
        # Create cache key
        cache_key = f"rate_limit:{limit_type}:{client_ip}"
        
        # Check current requests
        current_requests = cache.get(cache_key, 0)
        
        if current_requests >= limit['requests']:
            if request.path.startswith('/api/'):
                return JsonResponse({
                    'error': 'Rate limit exceeded. Please try again later.',
                    'retry_after': limit['window']
                }, status=429)
            else:
                return HttpResponse(
                    f"Rate limit exceeded. Please try again in {limit['window']} seconds.",
                    status=429
                )
        
        # Increment request count
        cache.set(cache_key, current_requests + 1, limit['window'])
        
        return None
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

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