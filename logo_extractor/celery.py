import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'logo_extractor.settings')

app = Celery('logo_extractor')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

app.conf.beat_schedule = {
    'refresh-old-logos-weekly': {
        'task': 'logosfinder.tasks.update_old_logos',
        'schedule': crontab(hour=9, minute=0, day_of_week=1),
    },
}

