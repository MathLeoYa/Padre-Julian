"""apps/core/serializers.py — Serializadores REST para los modelos base"""
from rest_framework import serializers
from .models import Proyecto, MapeoProyecto, HistorialPrioridad


class ProyectoSerializer(serializers.ModelSerializer):
    estado_display = serializers.CharField(source="get_estado_display", read_only=True)
    prioridad_display = serializers.CharField(source="get_prioridad_display", read_only=True)

    class Meta:
        model = Proyecto
        fields = [
            "id", "nombre", "codigo_interno", "redmine_id",
            "descripcion", "recurso_asignado", "dueno", "correo_dueno",
            "estado", "estado_display", "avance_porcentaje",
            "prioridad", "prioridad_display",
            "fecha_inicio", "fecha_fin_estimada", "fecha_actualizacion",
        ]
        read_only_fields = ["fecha_actualizacion"]


class MapeoProyectoSerializer(serializers.ModelSerializer):
    class Meta:
        model = MapeoProyecto
        fields = "__all__"
        read_only_fields = ["fecha_registro"]


class HistorialPrioridadSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistorialPrioridad
        fields = "__all__"
        read_only_fields = ["fecha"]
