"""config/urls.py — Rutas raíz del proyecto"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    # Spec #2: endpoints de webhooks e ingesta
    path("api/sync/", include("apps.sync.urls")),
    # Spec #3: endpoints de certificación y repriorización
    path("api/", include("apps.certification.urls")),
    # Core: tablero principal
    path("", include("apps.core.urls")),
]
