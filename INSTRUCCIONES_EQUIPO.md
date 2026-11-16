# GUÍA DE TRABAJO EN EQUIPO — METODOLOGÍA SDD
### Proyecto: Dashboard Gerencial PMO (Cooperativa Padre Julián Lorente)

---

## 👥 Asignación de Roles y Specs

| Miembro | Rol | Spec Asignado | Rama Git | Módulo / Carpeta |
| :--- | :--- | :--- | :--- | :--- |
| **Mateo** | **Líder de Equipo** | **Spec #1: Core & Stack Base** | `main` | `config/`, `apps/core/` |
| **Desarrollador 1** | Integrante | **Spec #2: Ingesta, Webhooks y Mapeo** | `feature/spec-2` | `apps/sync/` |
| **Desarrollador 2** | Integrante | **Spec #3: Certificación y Repriorización** | `feature/spec-3` | `apps/certification/` |

---

## 🚀 Flujo para el Resto del Equipo (Paso a Paso)

### 1. Clonar el repositorio y crear su rama
Cada desarrollador debe ejecutar en su terminal:
```bash
# Clonar
git clone <URL_DEL_REPOSITORIO>
cd Padre-Julian

# Crear y pasarse a su rama dedicada
# Desarrollador 1:
git checkout -b feature/spec-2

# Desarrollador 2:
git checkout -b feature/spec-3
```

### 2. Configuración del entorno local
```bash
# Crear y activar entorno virtual (opcional pero recomendado)
python -m venv venv
venv\Scripts\activate   # En Windows

# Instalar dependencias exactas
pip install -r requirements.txt

# Configurar variables de entorno
copy .env.example .env

# Correr migraciones base (generadas por el Líder)
python manage.py migrate

# Crear superusuario local
python manage.py createsuperuser

# Probar que el servidor arranca
python manage.py runserver
```

---

## 📋 Detalle de Trabajo para Cada Desarrollador

### 🔹 Para Desarrollador 1 (`feature/spec-2` en `apps/sync/`)
**Objetivo:** Automatizar la entrada de datos para que el PMO no tenga que pasar datos de Redmine a mano.
1. **Modelos:** No necesita crear un nuevo modelo de proyecto; debe importar `Proyecto` y `MapeoProyecto` desde `apps.core.models`.
2. **Webhooks (`apps/sync/views.py`):**
   - Crear endpoint POST `/api/sync/webhook/`.
   - Recibir el JSON de Redmine (cuando cambia una tarea/estado).
   - Validar si el proyecto está mapeado en `MapeoProyecto`.
   - Si no está mapeado, agregarlo con estado `pendiente` (cola de conciliación).
   - Si está mapeado, actualizar avance y estado en `Proyecto`.
3. **Parser de Excel (`apps/sync/services/excel_parser.py`):**
   - Crear función con `openpyxl` que lea el Excel inicial del PMO (columnas: Proyecto, Avance, Recurso, Dueño).
4. **Polling de respaldo (`apps/sync/tasks.py`):**
   - Crear tarea Celery programada que consulte la API REST de Redmine por si se cayó algún webhook.

---

### 🔹 Para Desarrollador 2 (`feature/spec-3` en `apps/certification/`)
**Objetivo:** Controlar el SLA de 5 días para pruebas de certificación y la repriorización con auditoría.
1. **Modelos (`apps/certification/models.py`):**
   - Crear modelo `RegistroCertificacion` con campos:
     - `proyecto` (FK a `core.Proyecto`)
     - `fecha_envio` (DateTimeField)
     - `fecha_limite` (DateTimeField, cálculo de +5 días)
     - `estado_certificacion` (Pendiente, Aprobado, Rechazado)
     - `atrasado` (BooleanField, default=False)
     - `observaciones` (TextField)
2. **Scheduler / SLA de 5 Días (`apps/certification/tasks.py`):**
   - Crear tarea periódica en Celery que revise diariamente proyectos en estado `certificacion`.
   - Si pasaron 5 días sin respuesta del dueño/certificador:
     - Marcar `atrasado = True`.
     - Disparar alerta por correo (`django.core.mail.send_mail`).
3. **Módulo de Repriorización (`apps/certification/views.py`):**
   - Endpoint POST `/api/proyectos/<id>/repriorizar/`.
   - Validar que el usuario tenga rol de `gestor` o `admin`.
   - Guardar el cambio y crear registro en `HistorialPrioridad` (de `apps.core.models`).
   - Sincronizar vía API REST con Redmine (con manejo de error y rollback si falla la API).

---

## 🛡️ Reglas Críticas de Convivencia Git
1. **Prohibido tocar `apps/core/models.py`:** Si alguien necesita un campo adicional, debe acordarlo previamente con el Líder (Mateo).
2. **Commits atómicos:** Usar mensajes claros, ej: `feat(sync): parser de excel implementado` o `feat(cert): tarea celery para reloj de 5 dias`.
3. **Integración vía Pull Requests:**
   - Nadie empuja directamente a `main`.
   - Se abre un PR desde `feature/spec-X` hacia `main`.
   - El líder Mateo revisa el PR y hace el merge.
