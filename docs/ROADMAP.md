# EcoRetiro — Roadmap

> Última actualización: Integración frontend-backend — Etapas 1 y 2 completadas ✅
> Stack: FastAPI + SQLAlchemy + PostgreSQL + Alembic + HTML/CSS/JS vanilla
> Tests backend: 26/26 passing | Cobertura: ~85%

---

## Estado general del proyecto

```
[1] Backend (FastAPI)        ← ✅ COMPLETADO
[2] Frontend (HTML/CSS/JS)   ← ✅ COMPLETADO (estático)
[3] Integración front-back   ← 🔄 EN CURSO (Etapas 1-2 completadas)
[4] Deploy                   ← 🔲 PENDIENTE
```

---

## Backend — Completado ✅

| Feature                          | Estado | Tests  | Notas                                      |
|----------------------------------|--------|--------|--------------------------------------------|
| Auth                             | ✅     | 4/4    | Registro, login, JWT                       |
| Feature 1 — Requests             | ✅     | 6/6    | 7 pasos completos + migración              |
| Feature 2 — Panel Operador       | ✅     | 2/2    | GET /requests, PATCH status, fixture op    |
| Feature 3 — Perfil de usuario    | ✅     | 5/5    | GET /users/me, PATCH /users/me             |
| Feature 4 — Notificaciones       | ✅     | 5/5    | CRUD interno, sin emails externos          |
| Feature 5 — Dashboard Admin      | ✅     | 3/3    | Estadísticas y métricas del sistema        |
| **Integración notificaciones**   | ✅     | 3/3    | Auto-notifica en create + update_status    |
| Deuda técnica Alta               | ✅     | —      | datetime.now(UTC), ConfigDict              |
| Deuda técnica Media              | ✅     | —      | pytest-cov, .env.test                      |
| Deuda técnica Baja               | ✅     | —      | operator_token fixture en conftest.py      |

### Integración de notificaciones automáticas ✅

| Evento                              | Mensaje                                           | Ubicación                         |
|-------------------------------------|---------------------------------------------------|-----------------------------------|
| Usuario crea una solicitud          | "Tu solicitud {tracking} fue recibida."           | `request_service.create()`        |
| Operador cambia estado de solicitud | "Tu solicitud {tracking} cambió a {estado}."      | `request_service.update_status()` |

- ✅ Mapper `STATUS_MESSAGES` con traducciones al español
- ✅ Import local de `notification_repository` en service
- ✅ Solo notifica en cambios de estado (no en asignaciones de vehículo/operador)

### Deuda técnica pendiente

| Prioridad | Ítem                                                              | Estado |
|-----------|-------------------------------------------------------------------|--------|
| Media     | Cobertura actual ~85% — identificar gaps y agregar tests faltantes| 🔲     |

---

## Frontend estático — Completado ✅

### Sistema de diseño
- **Estética:** retro-moderna (Win95/98 + moderno)
- **Fuentes:** Pixelify Sans + Inter
- **Colores:** magenta #ff006e | cyan #00f5ff | purple #8338ec | yellow #ffbe0b | green #06ffa5
- **Dark mode:** implementado via `[data-theme="dark"]` + toggle en titlebar, persiste en `ecoretiro-theme`

### Archivos del sistema
```
frontend/
├── css/retro-modern.css     ✅ estilos globales + dark mode
├── js/window-system.js      ✅ botones ventana + theme toggle + desktop icons
├── js/api.js                ✅ cliente API (auth + requests + notifications + user)
└── pages/
    ├── login.html           ✅
    ├── home.html            ✅
    ├── nueva-solicitud.html ✅
    ├── tracking.html        ✅
    ├── panel-operador.html  ✅
    ├── dashboard-admin.html ✅
    └── perfil.html          ✅
```

### Comportamiento del sistema de ventanas
- Botón `_` → minimiza con animación
- Botón `□` → toggle maximized
- Botón `×` → fade out + desktop icons contextuales:
  - Sin token: solo ícono 🔑 Iniciar Sesión → login.html
  - Con token: taskbar con 🏠 ➕ 📦 👤 🔒 (logout limpia token)

---

## Integración Frontend-Backend — En curso 🔄

### Etapa 1 — Auth ✅
| Tarea | Estado |
|-------|--------|
| `api.js` con `EcoRetiroAPI` (login, register, authFetch, token helpers) | ✅ |
| `login.html` integrado — login + registro en mismo form (toggle) | ✅ |
| Auth guard: sin token → redirect a login | ✅ |
| Errores inline (sin alert()), botón deshabilitado durante fetch | ✅ |
| Auto-login tras registro exitoso | ✅ |
| CORS configurado para `http://127.0.0.1:5500` y `http://localhost:5500` | ✅ |

### Etapa 2 — Home ✅
| Tarea | Estado |
|-------|--------|
| `getCurrentUser()` → nombre y email reales en header | ✅ |
| `getMyRequests()` → request cards reales con STATUS_MAP | ✅ |
| `getMyNotifications()` → badge con conteo de no leídas | ✅ |
| Stats reales (total, completadas, en proceso) | ✅ |
| Loading state + empty state + error state | ✅ |
| `escapeHtml()` para prevenir XSS | ✅ |

### Etapa 3 — Nueva Solicitud 🔲
- POST /requests con form integrado

### Etapa 4 — Tracking 🔲
- GET /track/{tracking_number} — público, sin token

### Etapa 5 — Perfil 🔲
- GET /users/me + PATCH /users/me

### Etapa 6 — Panel Operador 🔲
- GET /requests + PATCH /requests/{id}/status

### Etapa 7 — Dashboard Admin 🔲
- GET /admin/stats

---

## Convenciones del proyecto

### Backend
- **Routers:** solo HTTP + delegación al service. Nunca `db.query()` en router.
- **Services:** lógica de negocio. Nunca HTTP/status_code acá.
- **Repositories:** solo acceso a DB. Nada de reglas de negocio.
- **Excepciones:** siempre desde `core/exceptions.py`. Nunca inline.
- **Auth:** `get_current_user` para USER, `require_role("OPERATOR")` o `require_role("ADMIN")` para roles elevados.
- **Tests:** siempre con `StaticPool` + importar modelos antes de `create_all`.
- **Schemas:** `ConfigDict(from_attributes=True)`, nunca exponer `password_hash`.
- **Nombres:** `user_schema.py`, `request_repository.py`, `notification_service.py`, etc.
- **datetime:** siempre `datetime.now(timezone.utc)`, nunca `datetime.utcnow()`.

### Frontend
- **Token:** `localStorage.getItem('ecoretiro-token')`
- **Auth guard:** verificar token al inicio de cada página protegida
- **401:** `EcoRetiroAPI.redirectToLogin()` — limpia token y redirige
- **XSS:** usar `escapeHtml()` para cualquier dato del backend renderizado en innerHTML
- **Live Server:** siempre puerto 5500, nunca `file://`
- **Imports:** `api.js` siempre antes de `window-system.js`
