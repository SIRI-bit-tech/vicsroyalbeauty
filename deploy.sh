#!/bin/bash

# Production Deployment Script for Vics Royal Beauty
# This script sets up the production environment

set -e

echo "🚀 Starting production deployment..."

# Check if we're in the right directory
if [ ! -f "manage.py" ]; then
    echo "❌ Error: manage.py not found. Please run this script from the project root."
    exit 1
fi

# Install/update dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Run database migrations
echo "🗄️ Running database migrations..."
python manage.py migrate

# Create superuser if it doesn't exist
echo "👤 Checking superuser..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser('admin', 'admin@vicsroyalbeauty.com', 'changeme123')
    print('Superuser created: admin/changeme123')
else:
    print('Superuser already exists')
"

# Clear cache
echo "🧹 Clearing cache..."
python manage.py shell -c "from django.core.cache import cache; cache.clear()"

# Check system health
echo "🏥 Checking system health..."
python manage.py shell -c "
from django.db import connection
from django.core.cache import cache
import redis

# Database check
try:
    with connection.cursor() as cursor:
        cursor.execute('SELECT 1')
    print('✅ Database: OK')
except Exception as e:
    print(f'❌ Database: {e}')

# Redis check
try:
    redis_client = redis.from_url('redis://localhost:6379/0')
    redis_client.ping()
    print('✅ Redis: OK')
except Exception as e:
    print(f'❌ Redis: {e}')
"

echo "✅ Deployment completed successfully!"
echo ""
echo "🔧 Next steps:"
echo "1. Update environment variables in production"
echo "2. Configure CloudFlare CDN"
echo "3. Set up SSL certificates"
echo "4. Configure monitoring and alerts"
echo "5. Test all functionality"
echo ""
echo "🌐 Your site should now be ready for production traffic!" 