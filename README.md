# Dashboard Gerencial PMO
### Cooperativa Padre Julián Lorente — Área de Tecnología

Sistema web que integra automáticamente Redmine y la matriz Excel del PMO para eliminar la sincronización manual de proyectos de TI.

---

## Stack tecnológico
| Componente | Tecnología |
|---|---|
| Backend | Python 3.14 + Django 5.2 |
| API REST | Django REST Framework |
| Scheduler / tareas | Celery + Redis |
| BD del dashboard | SQLite (dev) → PostgreSQL/MySQL (prod) |
| BD Redmine | MySQL (solo lectura) |
| Frontend | Bootstrap 5 + Django Templates |

---

## Estructura del proyecto

```
Padre-Julian/
├── apps/
│   ├── core/           ← Spec #1 (Líder): modelos base, roles, tablero
│   ├── sync/           ← Spec #2: webhooks, polling, mapeo, conciliación
│   └── certification/  ← Spec #3: certificación SLA 5 días, repriorización
├── config/             ← Settings, URLs, Celery
├── templates/          ← HTML con Bootstrap
├── static/             ← CSS/JS estáticos
├── requirements.txt
└── .env.example
```

---

## Instalación y arranque (desarrollo)

```bash
# 1. Clonar el repositorio
git clone <URL-del-repo>
cd Padre-Julian

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar variables de entorno
cp .env.example .env
# Edita .env con tus valores reales

# 4. Aplicar migraciones
python manage.py migrate

# 5. Crear superusuario (Administrador)
python manage.py createsuperuser

# 6. Levantar el servidor
python manage.py runserver
```

Abre http://127.0.0.1:8000 para ver el tablero.
Abre http://127.0.0.1:8000/admin para el panel de administración (cola de conciliación, usuarios, proyectos).

---

## Flujo de ramas Git (SDD)

```
main                   ← rama principal (solo el líder hace merge)
├── feature/spec-1     ← Spec #1: stack base (COMPLETADO ✅)
├── feature/spec-2     ← Spec #2: ingesta y sincronización
└── feature/spec-3     ← Spec #3: certificación y repriorización
```

### Reglas de trabajo
- Cada integrante trabaja **exclusivamente** en su rama `feature/spec-X`.
- Para integrar: abrir un **Pull Request** hacia `main` con al menos una revisión aprobada.
- Los commits deben ser descriptivos: `feat(sync): agregar receptor de webhooks Redmine`.

---

## Responsabilidades por Spec

### Spec #1 — Stack base (Líder: Mateo) ✅ COMPLETADO
- Configuración Django, settings, Celery, variables de entorno.
- Modelos: `UsuarioDashboard`, `Proyecto`, `MapeoProyecto`, `HistorialPrioridad`.
- Panel de administración Django (cola de conciliación incluida).
- Template base y tablero inicial.

### Spec #2 — Ingesta y sincronización (Desarrollador 1)
- Rama: `feature/spec-2`
- **Lo que debe implementar en `apps/sync/`:**
  - Endpoint POST `/api/sync/webhook/` para recibir eventos de Redmine.
  - Job de polling periódico (Celery Beat, cada 5–10 min) que consulta la API de Redmine.
  - Parser de Excel (`openpyxl`) para la carga inicial de la matriz PMO.
  - Lógica de validación por ID de mapeo cruzando Excel con Redmine.
  - Gestión de la cola de conciliación (crear entradas en `MapeoProyecto`).
- **Modelos que puede usar de `apps.core`:** `Proyecto`, `MapeoProyecto`.
- **NO debe modificar** los modelos del `core`.

### Spec #3 — Certificación y repriorización (Desarrollador 2)
- Rama: `feature/spec-3`
- **Lo que debe implementar en `apps/certification/`:**
  - Modelo `RegistroCertificacion` (inicio, fecha límite, resultado, tiempo de respuesta).
  - Tarea Celery que detecta proyectos en estado `certificacion` con más de 5 días sin resultado y los marca como atrasados.
  - Envío de alertas por correo al dueño del requerimiento.
  - Endpoint POST `/api/proyectos/<id>/repriorizar/` con validación de rol y escritura del historial en `HistorialPrioridad`.
  - Lógica de rollback si la escritura en la API de Redmine falla.
- **Modelos que puede usar de `apps.core`:** `Proyecto`, `HistorialPrioridad`, `UsuarioDashboard`.
- **NO debe modificar** los modelos del `core`.

---

## Variables de entorno clave (.env)

Ver `.env.example` para la lista completa. Las más importantes para empezar:

| Variable | Descripción |
|---|---|
| `SECRET_KEY` | Clave secreta de Django (obligatoria) |
| `DEBUG` | `True` en desarrollo, `False` en producción |
| `REDMINE_URL` | URL base de la instancia Redmine |
| `REDMINE_API_KEY` | Token de API de Redmine |
| `CELERY_BROKER_URL` | URL de Redis para Celery |
