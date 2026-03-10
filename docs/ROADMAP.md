# EcoRetiro — Roadmap

> Última actualización: Integración de notificaciones automáticas completada ✅
> Stack: FastAPI + SQLAlchemy + PostgreSQL + Alembic
> Tests: 26/26 passing | Cobertura: ~85%

---

## Estado actual del backend

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

---

## Etapas del proyecto

```
[1] Backend (FastAPI)        ← ✅ COMPLETADO
[2] Frontend (HTML/CSS/JS)   ← siguiente
[3] Integración frontend-backend
[4] Deploy
```

---

## Backend — Completado ✅

### Feature 5 — Dashboard / Estadísticas (ADMIN) ✅
Endpoints para que ADMIN vea métricas del sistema.

| Paso | Tarea                                                        | Estado |
|------|--------------------------------------------------------------|--------|
| 1    | Sin modelo nuevo (usa Request, User, Notification existentes)| ✅     |
| 2    | Schema `DashboardStats` (totales, por estado, por operador)  | ✅     |
| 3    | Repository: queries de agregación                            | ✅     |
| 4    | Service: `get_stats(db)`                                     | ✅     |
| 5    | `GET /admin/stats` — solo ADMIN                              | ✅     |
| 6    | Tests con StaticPool                                         | ✅     |
| 7    | Sin migración (sin modelo nuevo)                             | ✅     |

---

### Integración de notificaciones automáticas ✅

Notificaciones disparadas automáticamente cuando ocurren estos eventos:

| Evento                              | Mensaje                                           | Ubicación                     | Estado |
|-------------------------------------|---------------------------------------------------|-------------------------------|--------|
| Usuario crea una solicitud          | "Tu solicitud {tracking} fue recibida."           | `request_service.create()`    | ✅     |
| Operador cambia estado de solicitud | "Tu solicitud {tracking} cambió a {estado}."      | `request_service.update_status()` | ✅ |

**Implementación:**
- ✅ Mapper `STATUS_MESSAGES` con traducciones al español
- ✅ Import local de `notification_repository` en service
- ✅ 3 tests de integración agregados
- ✅ Solo notifica en cambios de estado (no en asignaciones de vehículo/operador)

---

## Deuda técnica pendiente

| Prioridad | Ítem                                                              | Estado |
|-----------|-------------------------------------------------------------------|--------|
| Media     | Cobertura actual ~85% — identificar gaps y agregar tests faltantes| 🔲     |
| Baja      | Revisar si `back_populates` en todos los modelos está completo    | ✅     |

---

## Frontend (próxima etapa)

A encarar ahora que el backend está 100% funcional y testeado.

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
