import os
from celery import Celery
from kombu import Queue, Exchange


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')

celery_app = Celery('app',)

celery_app.config_from_object('django.conf:settings', namespace='CELERY')

celery_app.conf.beat_scheduler = 'django_celery_beat.schedulers:DatabaseScheduler'

celery_app.conf.update(
    broker_url='redis://redis:6379/0',
    task_queues=(
        Queue('celery', Exchange('celery'), routing_key='celery'),
    ),
)


celery_app.autodiscover_tasks()


celery_app.conf.update(
    timezone='America/Mexico_City',
    enable_utc=True,  
)
