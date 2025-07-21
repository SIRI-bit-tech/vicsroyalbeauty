#!/bin/bash
set -e

# Run migrations
python manage.py migrate --noinput

# Create superuser if it doesn't exist (email-based user model)
if [ "$DJANGO_SUPERUSER_EMAIL" ] && [ "$DJANGO_SUPERUSER_PASSWORD" ]; then
  python manage.py shell << END
from django.contrib.auth import get_user_model
User = get_user_model()
email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')
if not User.objects.filter(email=email).exists():
    User.objects.create_superuser(email=email, password=password)
    print(f"Superuser created: {email}/{password}")
else:
    print("Superuser already exists")
END
fi

# Collect static files (only for web)
if [ "$1" = "gunicorn" ]; then
  python manage.py collectstatic --noinput
fi

# Execute the given command
exec "$@" 