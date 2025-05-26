import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'logo_extractor.settings')

app = Celery('logo_extractor')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()
