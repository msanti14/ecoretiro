# EcoRetiro — Roadmap y Tareas Pendientes

> Última actualización: Feature 3 (perfil de usuario) completada ✅
> Stack: FastAPI + SQLAlchemy + PostgreSQL + Alembic

---

## Estado actual

| Capa         | Feature: Requests | Notas                              |
|--------------|-------------------|------------------------------------|
| 1. Model     | ✅                | Request, StatusHistory, User       |
| 2. Schema    | ✅                | RequestCreate, RequestRead, etc.   |
| 3. Repository| ✅                | create_with_history, tracking      |
| 4. Service   | ✅                | request_service, tracking_service  |
| 5. Router    | ✅                | /requests + /track                 |
| 6. Tests     | ✅                | 8/8 passing                        |
| 7. Migration | ✅                | Alembic: requests + status_history |
| Feature: Perfil de Usuario  | ✅ | GET /users/me, PATCH /users/me, 5 tests |
---

## Paso 7 — Migración Alembic (SIGUIENTE)

### 🧑 Vos (estudiante)
- [ ] Verificar que Alembic esté instalado: `alembic --version`
- [ ] Verificar que `alembic/env.py` importe `Base` desde `backend.database`
- [ ] Revisar el archivo generado en `alembic/versions/` antes de aplicar
- [ ] Correr `alembic upgrade head` contra la DB de desarrollo
- [ ] Verificar en psql/DBeaver que las tablas `requests` y `status_history` existan

### 🤖 Cursor
- [ ] Generar la migración con `alembic revision --autogenerate -m "agrega tabla requests y status_history"`
- [ ] Verificar que incluya índice en `tracking_number`
- [ ] Verificar que el `downgrade()` sea reversible

### 🟣 Claude (yo)
- [ ] Revisar el archivo de migración generado si hay dudas
- [ ] Debuggear errores de Alembic si aparecen

**Prompt listo para Cursor:**
```
I added the requests feature (Request model + StatusHistory model).
Generate the correct Alembic migration and verify:
- The migration matches the model change exactly
- No existing data will be lost
- Required indexes are included (tracking_number)
- The migration is reversible (downgrade works)
```

---

## Features pendientes (orden sugerido)

Siguiendo el workflow: model → schema → repository → service → router → tests → migration

### Feature 2 — Panel de Operador
Endpoints para que OPERATOR/ADMIN gestionen solicitudes.

| Paso | Tarea                                         | Responsable |
|------|-----------------------------------------------|-------------|
| 5    | `GET /requests` (listar todas, solo OPERATOR) | Cursor      |
| 5    | `PATCH /requests/{id}/status` ya existe ✅    | —           |
| 5    | `GET /requests/{id}` ya existe ✅             | —           |
| 6    | Tests con usuario OPERATOR en conftest        | Cursor + vos|
| —    | Fixture `operator_headers()` en conftest.py   | Claude      |

### Feature 3 — Perfil de Usuario
Endpoints para que USER vea y edite su perfil.

| Paso | Tarea                                          | Estado |
|------|------------------------------------------------|--------|
| 1-2  | Ningún modelo nuevo necesario                  | ✅     |
| 3    | update_user en user_repository.py              | ✅     |
| 4    | get_me, update_me en user_service.py           | ✅     |
| 5    | GET /users/me, PATCH /users/me                 | ✅     |
| 6    | 5 tests — todos passing                        | ✅     |
| 7    | Migración no requerida (sin cambios en modelo) | ✅     |

### Feature 4 — Notificaciones (futuro)
Avisar al usuario cuando cambia el estado de su solicitud.

| Paso | Tarea                                         | Responsable |
|------|-----------------------------------------------|-------------|
| 1    | Model `Notification`                          | Cursor      |
| 3    | Repository + lógica de envío                  | Cursor      |
| 7    | Migración tabla notifications                 | Cursor      |

---

## Deuda técnica / mejoras pendientes

| Prioridad | Ítem                                                        | Responsable |
|-----------|-------------------------------------------------------------|-------------|
| Alta      | `datetime.utcnow()` deprecado → migrar a `datetime.now(UTC)` | Cursor     |✅
| Alta      | `class Settings(BaseSettings)` → migrar a `ConfigDict`      |Cursor       |✅
| Media     | Agregar `pytest-cov` y medir cobertura de tests             | Vos         |
| Media     | Variables de entorno para test (`.env.test`)                | Vos         |
| Baja      | Fixture `operator_headers()` en conftest para tests de rol  | Claude      |

---

## Convenciones del proyecto (recordatorio rápido)

- **Routers:** solo HTTP + delegación al service. Nunca `db.query()` en router.
- **Services:** lógica de negocio. Nunca HTTP/status_code acá.
- **Repositories:** solo acceso a DB. Nada de reglas de negocio.
- **Excepciones:** siempre desde `core/exceptions.py`. Nunca inline.
- **Auth:** `get_current_user_id` para USER, `require_operator_or_admin` para OPERATOR/ADMIN.
- **Tests:** siempre con `StaticPool` + importar modelos antes de `create_all`.

---

## Prompts de referencia rápida para Cursor

**Nueva feature:**
```
Following the workflow in ai_workflow.md, implement [feature].
Show me one layer at a time. Wait for my approval before moving to the next.
Reference ai_architecture.md for conventions.
```

**Debuggear error:**
```
This endpoint is failing: [método] [ruta]
Error: [mensaje]
Check against ai_architecture.md. Identify which layer has the problem.
Fix only that layer.
```

**Agregar validación:**
```
Add validation to [schema] for [campo]: [reglas].
Validation must be in the Pydantic schema only.
Add a test for the 422 failure case.
```
