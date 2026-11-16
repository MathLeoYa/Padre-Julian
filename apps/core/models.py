"""
apps/core/models.py  —  Spec #1
Modelos base del sistema: Usuario, Rol, Proyecto y Mapeo.
Los Spec #2 y #3 importan desde aquí; NO deben mover ni renombrar estas clases.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models


# ------------------------------------------------------------------
# 1. USUARIO EXTENDIDO CON ROL
# ------------------------------------------------------------------
class UsuarioDashboard(AbstractUser):
    """
    Reemplaza al User de Django para agregar el rol del sistema.
    La autenticación usa la cuenta centralizada (LDAP/AD) de la cooperativa;
    este modelo sincroniza el rol una vez que el usuario inicia sesión.
    """

    class Rol(models.TextChoices):
        ADMIN = "admin", "Administrador de TI"
        GESTOR = "gestor", "Gestor / PMO"
        LECTOR = "lector", "Lector"

    rol = models.CharField(
        max_length=10,
        choices=Rol.choices,
        default=Rol.LECTOR,
        verbose_name="Rol en el sistema",
    )

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_rol_display()})"

    # Helpers de permiso rápido
    @property
    def es_gestor(self):
        return self.rol in (self.Rol.GESTOR, self.Rol.ADMIN)

    @property
    def es_admin(self):
        return self.rol == self.Rol.ADMIN


# ------------------------------------------------------------------
# 2. PROYECTO (entidad central compartida entre todos los Specs)
# ------------------------------------------------------------------
class Proyecto(models.Model):
    """
    Representa un proyecto de TI de la cooperativa.
    Es la entidad que une la matriz PMO (Excel) con Redmine.
    """

    class Prioridad(models.IntegerChoices):
        ALTA = 1, "Alta (1)"
        MEDIA = 2, "Media (2)"
        BAJA = 3, "Baja (3)"

    class Estado(models.TextChoices):
        EN_CURSO = "en_curso", "En curso"
        CERTIFICACION = "certificacion", "En certificación"
        CERTIFICADO = "certificado", "Certificado"
        RECHAZADO = "rechazado", "Rechazado"
        COMPLETADO = "completado", "Completado"
        PAUSADO = "pausado", "Pausado"

    # Identificadores
    nombre = models.CharField(max_length=255, verbose_name="Nombre del proyecto")
    codigo_interno = models.CharField(
        max_length=50, unique=True, blank=True, null=True,
        verbose_name="Código interno (PMO)",
        help_text="Identificador único en la matriz Excel",
    )
    redmine_id = models.IntegerField(
        unique=True, blank=True, null=True,
        verbose_name="ID en Redmine",
    )

    # Datos del PMO (cargados desde Excel en la ingesta inicial)
    descripcion = models.TextField(blank=True, default="")
    recurso_asignado = models.CharField(max_length=255, blank=True, default="")
    dueno = models.CharField(
        max_length=255, blank=True, default="",
        verbose_name="Dueño del requerimiento",
        help_text="Usuario de negocio responsable de las pruebas de certificación",
    )
    correo_dueno = models.EmailField(
        blank=True, default="",
        verbose_name="Correo del dueño",
    )

    # Estado y avance (sincronizados desde Redmine)
    estado = models.CharField(
        max_length=20, choices=Estado.choices, default=Estado.EN_CURSO
    )
    avance_porcentaje = models.PositiveSmallIntegerField(
        default=0, verbose_name="Avance (%)"
    )
    prioridad = models.IntegerField(
        choices=Prioridad.choices, default=Prioridad.MEDIA
    )

    # Fechas
    fecha_inicio = models.DateField(blank=True, null=True)
    fecha_fin_estimada = models.DateField(blank=True, null=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    # Relaciones
    responsable = models.ForeignKey(
        UsuarioDashboard,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="proyectos_asignados",
    )

    class Meta:
        verbose_name = "Proyecto"
        verbose_name_plural = "Proyectos"
        ordering = ["prioridad", "nombre"]

    def __str__(self):
        return f"[{self.codigo_interno}] {self.nombre} — {self.get_estado_display()}"


# ------------------------------------------------------------------
# 3. MAPEO PROYECTO  (cola de conciliación)
# ------------------------------------------------------------------
class MapeoProyecto(models.Model):
    """
    Tabla de equivalencias entre el nombre en Excel y el ID en Redmine.
    Cuando el sistema no puede emparejar automáticamente, registra
    el intento aquí y el PMO lo resuelve a mano (cola de conciliación).
    """

    class EstadoMapeo(models.TextChoices):
        PENDIENTE = "pendiente", "Pendiente — en cola de conciliación"
        CONFIRMADO = "confirmado", "Confirmado"
        DESCARTADO = "descartado", "Descartado (proyecto nuevo)"

    proyecto = models.OneToOneField(
        Proyecto,
        on_delete=models.CASCADE,
        related_name="mapeo",
        null=True, blank=True,
    )
    nombre_excel = models.CharField(max_length=255, verbose_name="Nombre en Excel")
    redmine_id = models.IntegerField(verbose_name="ID en Redmine")
    estado = models.CharField(
        max_length=15, choices=EstadoMapeo.choices, default=EstadoMapeo.PENDIENTE
    )
    notas = models.TextField(blank=True, default="")
    resuelto_por = models.ForeignKey(
        UsuarioDashboard,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="conciliaciones_resueltas",
    )
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_resolucion = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Mapeo de proyecto"
        verbose_name_plural = "Cola de conciliación"
        ordering = ["-fecha_registro"]

    def __str__(self):
        return f"{self.nombre_excel} ↔ Redmine #{self.redmine_id} [{self.get_estado_display()}]"


# ------------------------------------------------------------------
# 4. HISTORIAL DE PRIORIDAD (auditoría de cambios regulatorios)
# ------------------------------------------------------------------
class HistorialPrioridad(models.Model):
    """
    Registra cada cambio de prioridad: quién lo hizo, cuándo y por qué.
    Requerido por la volatilidad regulatoria de la cooperativa.
    """

    proyecto = models.ForeignKey(
        Proyecto, on_delete=models.CASCADE, related_name="historial_prioridades"
    )
    prioridad_anterior = models.IntegerField(choices=Proyecto.Prioridad.choices)
    prioridad_nueva = models.IntegerField(choices=Proyecto.Prioridad.choices)
    motivo = models.TextField(blank=True, default="")
    cambiado_por = models.ForeignKey(
        UsuarioDashboard, on_delete=models.SET_NULL, null=True
    )
    fecha = models.DateTimeField(auto_now_add=True)
    sincronizado_redmine = models.BooleanField(default=False)
    error_sincronizacion = models.TextField(blank=True, default="")

    class Meta:
        verbose_name = "Historial de prioridad"
        verbose_name_plural = "Historial de prioridades"
        ordering = ["-fecha"]

    def __str__(self):
        return (
            f"{self.proyecto.nombre}: "
            f"{self.prioridad_anterior} → {self.prioridad_nueva} "
            f"({self.fecha.strftime('%Y-%m-%d %H:%M')})"
        )
