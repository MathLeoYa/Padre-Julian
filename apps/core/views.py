"""apps/core/views.py — Vista del tablero gerencial"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Proyecto, MapeoProyecto


@login_required
def tablero(request):
    """Vista principal del dashboard gerencial."""
    proyectos = Proyecto.objects.select_related("responsable").order_by("prioridad", "nombre")
    conciliacion_pendiente = MapeoProyecto.objects.filter(estado="pendiente").count()

    context = {
        "proyectos": proyectos,
        "total_proyectos": proyectos.count(),
        "en_certificacion": proyectos.filter(estado="certificacion").count(),
        "conciliacion_pendiente": conciliacion_pendiente,
    }
    return render(request, "core/tablero.html", context)
