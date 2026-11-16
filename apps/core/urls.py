"""apps/core/urls.py — Rutas del tablero principal"""
from django.urls import path
from . import views

urlpatterns = [
    path("", views.tablero, name="tablero"),
]
