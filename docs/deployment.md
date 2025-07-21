# Deployment Guide

## Prerequisites
- Python 3.9+
- PostgreSQL
- Redis
- Node.js (for Tailwind CSS)

## Environment Setup
1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
npm install
```

3. Configure environment variables in `.env`:
```
DEBUG=False
SECRET_KEY=your_secret_key
DATABASE_URL=postgres://user:password@host:5432/dbname
REDIS_URL=redis://localhost:6379/0
GLITCHTIP_DSN=your_glitchtip_dsn
EMAIL_HOST_USER=your_email
EMAIL_HOST_PASSWORD=your_email_password
```

## Database Setup
1. Run migrations:
```bash
python manage.py migrate
```

2. Create superuser:
```bash
python manage.py createsuperuser
```

## Static Files
1. Collect static files:
```bash
python manage.py collectstatic --noinput
```

## Production Server
1. Configure Gunicorn:
```bash
gunicorn vics_royal.wsgi:application --bind 0.0.0.0:8000
```