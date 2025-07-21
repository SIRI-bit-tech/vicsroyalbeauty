# Production Deployment Guide

## Environment Variables Required

Create a `.env` file in your project root with the following variables:

```bash
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=False
ENVIRONMENT=production
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database
DATABASE_URL=postgresql://username:password@host:port/database_name

# Redis Configuration
REDIS_URL=redis://localhost:6379

# Cloudinary Configuration
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret

# Glitchtip (Sentry) Configuration
GLITCHTIP_DSN=https://your-glitchtip-dsn

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Security Settings
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Database Setup
```bash
python manage.py migrate
python manage.py collectstatic
```

### 3. Redis Setup
- Install Redis on your server
- Ensure Redis is running on the configured port
- The application uses Redis for:
  - Session storage
  - Application caching
  - Long-term caching

### 4. Cloudinary Setup
- Create a Cloudinary account
- Get your cloud name, API key, and API secret
- All media uploads will be stored on Cloudinary
- Images are automatically optimized and served via CDN

### 5. Glitchtip Setup
- Create a Glitchtip account
- Get your DSN (Data Source Name)
- Error tracking and performance monitoring will be enabled

### 6. Production Server
- Use Gunicorn as WSGI server
- Configure Nginx as reverse proxy
- Enable HTTPS with SSL certificates
- Set up proper security headers

## Cloudinary Integration

### ✅ Model Updates
The following models have been updated to use Cloudinary:

- **Category Model**: Uses CloudinaryField with automatic optimization
- **ProductImage Model**: Uses CloudinaryField with multiple size options
- **CustomUser Model**: Profile images use CloudinaryField with face detection

### ✅ Helper Methods
Each model includes optimized helper methods:

```python
# Category Model
category.image_url  # Optimized 400x300 image

# ProductImage Model
product_image.thumbnail_url  # 150x150 thumbnail
product_image.medium_url     # 400x400 medium
product_image.large_url      # 800x800 large

# CustomUser Model
user.profile_image_url  # 200x200 with face detection
```

### ✅ Automatic Features
- **Single Upload**: Upload once, get multiple optimized formats
- **Auto Optimization**: Quality and format optimization
- **CDN Delivery**: Fast global image delivery
- **Face Detection**: Profile images automatically crop to faces
- **Responsive Images**: Different sizes for different contexts

## Features Enabled

### ✅ Error Monitoring
- Glitchtip (Sentry) integration for error tracking
- Performance monitoring and session replay
- User context in error reports

### ✅ Image Management
- Cloudinary integration for all media files
- Automatic image optimization
- CDN delivery for fast loading
- Single upload, multiple formats

### ✅ Caching
- Redis-based caching system
- Multiple cache backends:
  - Default cache (15 minutes)
  - Session cache (7 days)
  - Long-term cache (30 days)
- Session storage in Redis

### ✅ Security
- HTTPS enforcement in production
- Security headers enabled
- CSRF protection
- XSS protection
- Content type sniffing protection

### ✅ Performance
- Static file compression
- Image optimization
- Database connection pooling
- Redis connection pooling
- Caching middleware

## Monitoring

- **Error Tracking**: Glitchtip dashboard
- **Performance**: Glitchtip performance monitoring
- **Caching**: Redis monitoring
- **Images**: Cloudinary dashboard
- **Server**: Standard server monitoring tools

## Backup Strategy

- **Database**: Regular PostgreSQL backups
- **Media**: Cloudinary handles image backups
- **Code**: Git repository
- **Configuration**: Environment variables in secure storage 