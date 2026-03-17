# ARCHITECTURE.md — EcoRetiro

## Estructura de Carpetas

```
ecoretiro/
├── backend/
│   ├── main.py                      # Entry point FastAPI + CORS
│   ├── database.py                  # Conexión y sesión PostgreSQL
│   ├── models/                      # CAPA 1: SQLAlchemy ORM
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── request.py
│   │   ├── photo.py
│   │   └── status_history.py
│   ├── schemas/                     # CAPA 2: Contratos de API (Pydantic)
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── request.py
│   │   └── tracking.py
│   ├── repositories/                # CAPA 3: Acceso a base de datos
│   │   ├── __init__.py
│   │   ├── user_repository.py
│   │   ├── request_repository.py
│   │   └── status_history_repository.py
│   ├── services/                    # CAPA 4: Lógica de negocio
│   │   ├── __init__.py
│   │   ├── tracking_service.py
│   │   ├── vehicle_service.py
│   │   └── cloudinary_service.py
│   ├── routers/                     # CAPA 5: HTTP / Endpoints
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── requests.py
│   │   └── tracking.py
│   └── core/
│       ├── config.py                # Settings desde .env
│       ├── security.py              # JWT utils
│       ├── dependencies.py          # get_db(), get_current_user()
│       └── exceptions.py            # HTTPExceptions reutilizables
├── tests/
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_requests.py
│   └── test_tracking.py
├── frontend/
│   ├── index.html
│   ├── solicitud.html
│   ├── tracking.html
│   ├── dashboard.html
│   ├── login.html
│   ├── css/styles.css
│   └── js/
│       ├── api.js
│       ├── tracking.js
│       └── map.js
├── docs/
│   └── ai/
│       ├── ai_architecture.md
│       ├── ai_prompts.md
│       └── ai_workflow.md
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
├── alembic.ini
├── PROJECT.md
├── ARCHITECTURE.md
├── AI_RULES.md
└── AI_PROJECT_PROMPT.md
```

---

## Capas y Responsabilidades

```
routers/ → services/ → repositories/ → models/
```

| Capa | Responsabilidad | Puede llamar a | NUNCA llama a |
|------|----------------|----------------|---------------|
| `routers/` | HTTP: recibir, validar schema, delegar, responder | `services/` | `repositories/`, `db` directamente |
| `services/` | Lógica de negocio, reglas, orquestación | `repositories/` | `db.query()` directamente |
| `repositories/` | Todas las queries a PostgreSQL | `models/`, `db` | `services/`, `routers/` |
| `models/` | Definición de tablas SQLAlchemy | — | Nada |
| `schemas/` | Validación entrada/salida con Pydantic | — | Nada |

---

## Convención de Nombres de Archivos

| Tipo | Patrón | Ejemplo |
|------|--------|---------|
| Modelo | `<entidad>.py` | `request.py` |
| Schema | `<entidad>.py` | `request.py` |
| Repository | `<entidad>_repository.py` | `request_repository.py` |
| Service | `<entidad>_service.py` | `tracking_service.py` |
| Router | `<entidad>.py` | `requests.py` |
| Test | `test_<entidad>.py` | `test_requests.py` |

---

## Convención de Nombres de Schemas Pydantic

| Sufijo | Uso |
|--------|-----|
| `Create` | Entrada del usuario (POST body) |
| `Read` | Respuesta al usuario |
| `Update` | Actualización parcial (PATCH body) |

Ejemplo: `RequestCreate`, `RequestRead`, `RequestUpdate`

---

## Modelo de Datos

### Users
```
id              | UUID, PK
name            | VARCHAR(100), requerido, min 2 chars
email           | VARCHAR(150), UNIQUE, requerido
password_hash   | VARCHAR(255), requerido
role            | ENUM: USER / OPERATOR / ADMIN, default: USER
phone           | VARCHAR(20), opcional
created_at      | TIMESTAMP, auto
```

### Requests
```
id                  | UUID, PK
tracking_number     | VARCHAR(30), UNIQUE, auto-generado
user_id             | FK → Users
address             | TEXT, requerido
lat                 | FLOAT, opcional
lng                 | FLOAT, opcional
description         | TEXT, min 10 chars
material_type       | ENUM, requerido
estimated_volume    | ENUM: SMALL / MEDIUM / LARGE, requerido
pickup_date         | DATE, no pasada
pickup_time_range   | ENUM: MORNING / AFTERNOON / EVENING
current_status      | ENUM, default: REQUESTED
vehicle_assigned    | ENUM: DUCATO / AUTO | NULL
operator_id         | FK → Users | NULL
created_at          | TIMESTAMP, auto
updated_at          | TIMESTAMP, auto
```

### Photos
```
id              | UUID, PK
request_id      | FK → Requests
image_url       | TEXT
cloudinary_id   | VARCHAR(100)
uploaded_at     | TIMESTAMP, auto
```

### StatusHistory
```
id              | UUID, PK
request_id      | FK → Requests
status          | ENUM
updated_by      | FK → Users
notes           | TEXT, opcional
timestamp       | TIMESTAMP, auto
```

---

## Estados y Transiciones

```
REQUESTED → SCHEDULED → IN_ROUTE → COLLECTED → CLASSIFIED → RECOVERED
                                                           ↘ SENT_TO_RECYCLING
                                                                    ↓
                                                                COMPLETED
```

```python
ALLOWED_TRANSITIONS = {
    "REQUESTED":         ["SCHEDULED"],
    "SCHEDULED":         ["IN_ROUTE"],
    "IN_ROUTE":          ["COLLECTED"],
    "COLLECTED":         ["CLASSIFIED"],
    "CLASSIFIED":        ["RECOVERED", "SENT_TO_RECYCLING"],
    "RECOVERED":         ["COMPLETED"],
    "SENT_TO_RECYCLING": ["COMPLETED"],
    "COMPLETED":         [],
}
```

---

## Rangos Horarios

| Valor | Franja |
|-------|--------|
| MORNING | 8:00 — 12:00 |
| AFTERNOON | 12:00 — 17:00 |
| EVENING | 17:00 — 20:00 |

---

## Tipos de Material

```
COMPUTADORA | MONITOR | TELEVISOR | IMPRESORA | CELULAR | TABLET |
ELECTRODOMESTICO | CABLE | PLACA_CIRCUITO | PILA_BATERIA | OTRO
```

---

## Lógica de Asignación de Vehículo

| estimated_volume | Vehículo asignado | Sobreescribible |
|-----------------|-------------------|-----------------|
| SMALL | AUTO | Sí (OPERATOR) |
| MEDIUM | AUTO | Sí (OPERATOR) |
| LARGE | DUCATO | Sí (OPERATOR) |

---

## Generación del tracking_number

- Formato: `ECO-USHUAIA-{AÑO}-{SECUENCIA_5_DIGITOS}`
- Ejemplo: `ECO-USHUAIA-2026-00034`
- Secuencia anual (se reinicia cada año)
- Generado dentro de la transacción de creación (atómica)

---

## Transacciones Críticas

### Crear solicitud (atómica)
1. Crear registro en `requests`
2. Insertar estado `REQUESTED` en `status_history`
3. Asignar vehículo automáticamente

### Cambiar estado (atómica)
1. Actualizar `current_status` en `requests`
2. Insertar registro en `status_history`

Siempre usar `db.flush()` + `db.commit()` en bloque `try/except` con `db.rollback()`.

---

## Endpoints

```
POST   /auth/register
POST   /auth/login

POST   /requests                    auth: USER+
GET    /requests/me                 auth: USER+
GET    /requests/{id}               auth: USER+
PATCH  /requests/{id}/status        auth: OPERATOR+

GET    /track/{tracking_number}     público, sin auth

GET    /dashboard/stats             auth: ADMIN
```

### Respuesta de tracking

```json
{
  "tracking_number": "ECO-USHUAIA-2026-00034",
  "current_status": "IN_ROUTE",
  "material_type": "COMPUTADORA",
  "pickup_date": "2026-03-10",
  "pickup_time_range": "MORNING",
  "vehicle_assigned": "AUTO",
  "history": [
    {"status": "REQUESTED",  "timestamp": "2026-03-08T21:00:00"},
    {"status": "SCHEDULED",  "timestamp": "2026-03-09T09:00:00"},
    {"status": "IN_ROUTE",   "timestamp": "2026-03-10T10:30:00"}
  ]
}
```

---

## Roles y Permisos

| Acción | USER | OPERATOR | ADMIN |
|--------|------|----------|-------|
| Crear solicitud | ✅ | ✅ | ✅ |
| Ver mis solicitudes | ✅ | ✅ | ✅ |
| Ver todas las solicitudes | ❌ | ✅ | ✅ |
| Cambiar estado | ❌ | ✅ | ✅ |
| Asignar vehículo | ❌ | ✅ | ✅ |
| Ver dashboard / stats | ❌ | ❌ | ✅ |
| Gestionar usuarios | ❌ | ❌ | ✅ |

---

## Variables de Entorno

```env
DATABASE_URL=postgresql://usuario:tu_contrasena@localhost:5432/ecoretiro
SECRET_KEY=cambia_esto_por_una_clave_segura
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
CLOUDINARY_CLOUD_NAME=
CLOUDINARY_API_KEY=
CLOUDINARY_API_SECRET=
```

---

## .gitignore

```gitignore
entorno/
venv/
.env
__pycache__/
*.pyc
*.pyo
.Python
*.egg-info/
dist/
build/
.pytest_cache/
test.db
.vscode/
.idea/
*.swp
.DS_Store
Thumbs.db
```
