"""
config/celery.py  —  Configuración de Celery para tareas en segundo plano
(polling de respaldo, reloj de 5 días de certificación)
"""

import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("dashboard_pmo")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
