# EcoRetiro — Roadmap

> Última actualización: Feature 4 (notificaciones internas) completada ✅
> Stack: FastAPI + SQLAlchemy + PostgreSQL + Alembic
> Tests: 20/20 passing | Cobertura: ~81%

---

## Estado actual del backend

| Feature                          | Estado | Tests  | Notas                                      |
|----------------------------------|--------|--------|--------------------------------------------|
| Auth                             | ✅     | 4/4    | Registro, login, JWT                       |
| Feature 1 — Requests             | ✅     | 6/6    | 7 pasos completos + migración              |
| Feature 2 — Panel Operador       | ✅     | 2/2    | GET /requests, PATCH status, fixture op    |
| Feature 3 — Perfil de usuario    | ✅     | 5/5    | GET /users/me, PATCH /users/me             |
| Feature 4 — Notificaciones       | ✅     | 5/5    | CRUD interno, sin emails externos          |
| Deuda técnica Alta               | ✅     | —      | datetime.now(UTC), ConfigDict              |
| Deuda técnica Media              | ✅     | —      | pytest-cov, .env.test                      |
| Deuda técnica Baja               | ✅     | —      | operator_token fixture en conftest.py      |

---

## Etapas del proyecto

```
[1] Backend (FastAPI)        ← estamos acá
[2] Integración notificaciones
[3] Frontend (HTML/CSS/JS)
[4] Integración frontend-backend
[5] Deploy
```

---

## Backend — Features pendientes

### Feature 5 — Dashboard / Estadísticas (ADMIN)
Endpoints para que ADMIN vea métricas del sistema.

| Paso | Tarea                                                        | Responsable |
|------|--------------------------------------------------------------|-------------|
| 1    | Sin modelo nuevo (usa Request, User, Notification existentes)| —           |
| 2    | Schema `DashboardStats` (totales, por estado, por operador)  | Cursor      |
| 3    | Repository: queries de agregación                            | Cursor      |
| 4    | Service: `get_stats(db)`                                     | Cursor      |
| 5    | `GET /admin/stats` — solo ADMIN                              | Cursor      |
| 6    | Tests con StaticPool                                         | Cursor + vos|
| 7    | Sin migración (sin modelo nuevo)                             | —           |

**Prompt para Cursor:**
```
Following the workflow in docs/ai/ai_workflow.md, implement Feature 5 — Admin Dashboard.
Read docs/ai/ai_architecture.md for conventions.
No new model needed — use existing Request, User, Notification models.
Start with Step 2 — Schema DashboardStats in backend/schemas/dashboard_schema.py.
Include: total_requests, requests_by_status (dict), total_users, total_notifications_unread.
Wait for my approval before moving to the next layer.
```

---

### Integración de notificaciones en features existentes

Disparar `notification_repository.create()` automáticamente cuando ocurran estos eventos:

| Evento                              | Mensaje sugerido                                      | Dónde agregar              |
|-------------------------------------|-------------------------------------------------------|----------------------------|
| Usuario crea una solicitud          | "Tu solicitud {tracking} fue recibida."               | `request_service.create()` |
| Operador cambia estado de solicitud | "Tu solicitud {tracking} cambió a {estado}."          | `request_service.update_status()` |
| Operador se asigna a una solicitud  | "Un operador fue asignado a tu solicitud {tracking}." | `request_service.assign_operator()` |

> ⚠️ Hacer esto **después de Feature 5** para no mezclar cambios.

---

## Deuda técnica pendiente

| Prioridad | Ítem                                                              | Estado |
|-----------|-------------------------------------------------------------------|--------|
| Media     | Cobertura actual ~81% — identificar gaps y agregar tests faltantes| 🔲     |
| Baja      | Revisar si `back_populates` en todos los modelos está completo    | ✅ hecho en Feature 4 |

---

## Frontend (próxima etapa)

A encarar cuando el backend esté 100% funcional y testeado.

| Pantalla                  | Rol        | Notas                        |
|---------------------------|------------|------------------------------|
| Login / Registro          | Todos      |                              |
| Panel de usuario          | USER       | Requests + notificaciones    |
| Crear solicitud           | USER       |                              |
| Seguimiento de solicitud  | USER       | Por tracking number          |
| Panel de operador         | OPERATOR   | Lista + cambio de estado     |
| Dashboard estadísticas    | ADMIN      | Feature 5                    |
| Perfil de usuario         | USER       |                              |

---

## Convenciones del proyecto (recordatorio rápido)

- **Routers:** solo HTTP + delegación al service. Nunca `db.query()` en router.
- **Services:** lógica de negocio. Nunca HTTP/status_code acá.
- **Repositories:** solo acceso a DB. Nada de reglas de negocio.
- **Excepciones:** siempre desde `core/exceptions.py`. Nunca inline.
- **Auth:** `get_current_user` para USER, `require_role("OPERATOR")` o `require_role("ADMIN")` para roles elevados.
- **Tests:** siempre con `StaticPool` + importar modelos antes de `create_all`.
- **Schemas:** `ConfigDict(from_attributes=True)`, nunca exponer `password_hash`.
- **Nombres:** `user_schema.py`, `request_repository.py`, `notification_service.py`, etc.
- **datetime:** siempre `datetime.now(timezone.utc)`, nunca `datetime.utcnow()`.
