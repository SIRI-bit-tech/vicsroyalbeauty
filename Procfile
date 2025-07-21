web: gunicorn vics_royal.wsgi --log-file - --workers 4 --worker-class gevent --worker-connections 1000 --max-requests 1000 --max-requests-jitter 100
worker: celery -A vics_royal worker --loglevel=info --concurrency=4
beat: celery -A vics_royal beat --loglevel=info
