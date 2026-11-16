"""apps/core/admin.py — Panel de administración Django"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import UsuarioDashboard, Proyecto, MapeoProyecto, HistorialPrioridad


@admin.register(UsuarioDashboard)
class UsuarioDashboardAdmin(UserAdmin):
    list_display = ("username", "get_full_name", "email", "rol", "is_active")
    list_filter = ("rol", "is_active")
    fieldsets = UserAdmin.fieldsets + (
        ("Rol en el Dashboard", {"fields": ("rol",)}),
    )


@admin.register(Proyecto)
class ProyectoAdmin(admin.ModelAdmin):
    list_display = (
        "codigo_interno", "nombre", "estado", "prioridad",
        "avance_porcentaje", "recurso_asignado", "dueno", "fecha_actualizacion",
    )
    list_filter = ("estado", "prioridad")
    search_fields = ("nombre", "codigo_interno", "recurso_asignado", "dueno")
    ordering = ("prioridad", "nombre")


@admin.register(MapeoProyecto)
class MapeoProyectoAdmin(admin.ModelAdmin):
    list_display = ("nombre_excel", "redmine_id", "estado", "resuelto_por", "fecha_registro")
    list_filter = ("estado",)
    search_fields = ("nombre_excel",)
    list_editable = ("estado",)  # El PMO resuelve la conciliación directo desde la lista


@admin.register(HistorialPrioridad)
class HistorialPrioridadAdmin(admin.ModelAdmin):
    list_display = (
        "proyecto", "prioridad_anterior", "prioridad_nueva",
        "cambiado_por", "fecha", "sincronizado_redmine",
    )
    list_filter = ("sincronizado_redmine",)
    readonly_fields = ("fecha",)
