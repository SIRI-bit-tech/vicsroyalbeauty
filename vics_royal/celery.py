import os
from celery import Celery
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vics_royal.settings')

app = Celery('vics_royal')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

# Celery Configuration
app.conf.update(
    # Broker settings
    broker_url=os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
    result_backend=os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
    
    # Task settings
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    
    # Worker settings
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    
    # Task routing
    task_routes={
        'core.tasks.*': {'queue': 'default'},
        'orders.tasks.*': {'queue': 'orders'},
        'products.tasks.*': {'queue': 'products'},
    },
    
    # Beat schedule for periodic tasks
    beat_schedule={
        'cleanup-expired-sessions': {
            'task': 'core.tasks.cleanup_expired_sessions',
            'schedule': 3600.0,  # Every hour
        },
        'send-newsletter-digest': {
            'task': 'core.tasks.send_newsletter_digest',
            'schedule': 86400.0,  # Daily
        },
        'update-product-cache': {
            'task': 'products.tasks.update_product_cache',
            'schedule': 1800.0,  # Every 30 minutes
        },
    },
    
    # Result backend settings
    result_expires=3600,  # 1 hour
    result_backend_transport_options={
        'master_name': "mymaster",
        'visibility_timeout': 3600,
    },
)

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}') 