import os
from celery import Celery

# set the Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'transaction_simulation.settings')

# create Celery app and configure it from Django settings
app = Celery('transaction_simulation')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(['transactions'])
