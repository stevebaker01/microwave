from __future__ import absolute_import
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'microwave.settings')

from django.conf import settings

stalk = Celery('microwave', backend='rpc://', broker='amqp://localhost')
stalk.config_from_object('django.conf:settings')
stalk.autodiscover_tasks(lambda: settings.INSTALLED_APPS)