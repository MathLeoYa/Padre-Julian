"""
config/settings.py  —  Spec #1: Configuración base del proyecto
Dashboard Gerencial PMO · Cooperativa Padre Julián Lorente
"""

import environ
import os
from pathlib import Path

# ------------------------------------------------------------------
# Rutas
# ------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# ------------------------------------------------------------------
# Variables de entorno  (.env)
# ------------------------------------------------------------------
env = environ.Env(
    DEBUG=(bool, True),
)
environ.Env.read_env(BASE_DIR / ".env")

# ------------------------------------------------------------------
# Seguridad
# ------------------------------------------------------------------
SECRET_KEY = env("SECRET_KEY")
DEBUG = env("DEBUG")
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])

# ------------------------------------------------------------------
# Apps instaladas
# ------------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Librerías de terceros
    "rest_framework",
    "django_celery_beat",
    # Apps del proyecto
    "apps.core",           # Spec #1 — modelos base, roles, autenticación
    "apps.sync",           # Spec #2 — ingesta, webhooks, mapeo, conciliación
    "apps.certification",  # Spec #3 — certificación, SLA 5 días, repriorización
]

# ------------------------------------------------------------------
# Middleware
# ------------------------------------------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

# ------------------------------------------------------------------
# Templates
# ------------------------------------------------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# ------------------------------------------------------------------
# Base de datos principal del dashboard (SQLite en desarrollo)
# ------------------------------------------------------------------
DATABASES = {
    "default": env.db("DATABASE_URL", default="sqlite:///db.sqlite3"),
    # Conexión a Redmine (MySQL, solo lectura — usada por Spec #2)
    "redmine": {
        "ENGINE": "django.db.backends.mysql",
        "HOST": env("REDMINE_DB_HOST", default="localhost"),
        "PORT": env("REDMINE_DB_PORT", default="3306"),
        "NAME": env("REDMINE_DB_NAME", default="redmine"),
        "USER": env("REDMINE_DB_USER", default=""),
        "PASSWORD": env("REDMINE_DB_PASSWORD", default=""),
        "OPTIONS": {"charset": "utf8mb4"},
    },
}

# ------------------------------------------------------------------
# Autenticación — modelo de usuario extendido
# ------------------------------------------------------------------
AUTH_USER_MODEL = "core.UsuarioDashboard"

# ------------------------------------------------------------------
# Django REST Framework
# ------------------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}

# ------------------------------------------------------------------
# Celery (scheduler y tareas en segundo plano)
# ------------------------------------------------------------------
CELERY_BROKER_URL = env("CELERY_BROKER_URL", default="redis://localhost:6379/0")
CELERY_RESULT_BACKEND = env("CELERY_RESULT_BACKEND", default="redis://localhost:6379/0")
CELERY_TIMEZONE = "America/Bogota"
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"

# ------------------------------------------------------------------
# Redmine — API
# ------------------------------------------------------------------
REDMINE_URL = env("REDMINE_URL", default="http://localhost:3000")
REDMINE_API_KEY = env("REDMINE_API_KEY", default="")

# ------------------------------------------------------------------
# Correo electrónico
# ------------------------------------------------------------------
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"  # Consola en DEV
EMAIL_HOST = env("EMAIL_HOST", default="localhost")
EMAIL_PORT = env.int("EMAIL_PORT", default=25)
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=False)
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="dashboard@cooperativa.com")

# ------------------------------------------------------------------
# Rocket.Chat (notificaciones opcionales)
# ------------------------------------------------------------------
ROCKETCHAT_URL = env("ROCKETCHAT_URL", default="")
ROCKETCHAT_USER = env("ROCKETCHAT_USER", default="")
ROCKETCHAT_PASSWORD = env("ROCKETCHAT_PASSWORD", default="")
ROCKETCHAT_CHANNEL = env("ROCKETCHAT_CHANNEL", default="#general")

# ------------------------------------------------------------------
# Internacionalización
# ------------------------------------------------------------------
LANGUAGE_CODE = "es-co"
TIME_ZONE = "America/Bogota"
USE_I18N = True
USE_TZ = True

# ------------------------------------------------------------------
# Archivos estáticos y de medios
# ------------------------------------------------------------------
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
