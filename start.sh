#!/usr/bin/env bash
# Render start script: migrate, create superuser, start Gunicorn

python manage.py migrate --noinput

# Create superuser if it doesn't exist
python manage.py shell << END
from django.contrib.auth import get_user_model
import os
User = get_user_model()
username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'adminpass')
if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f"Superuser created: {username}/{password}")
else:
    print("Superuser already exists")
END

# Start Gunicorn
gunicorn vics_royal.wsgi:application --bind 0.0.0.0:10000 