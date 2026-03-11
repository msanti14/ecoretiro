# docs/ai/ai_workflow.md — Flujo de Desarrollo

> Última actualización: Integración frontend-backend iniciada. Etapas 1-2 completadas.
> Stack real: SQLAlchemy 2.0 con `Mapped`.

---

## Orden de implementación backend

Para cada feature nueva, implementar siempre en este orden:

```
1. model → 2. schema → 3. repository → 4. service → 5. router → 6. tests → 7. migration
```

Si la feature no requiere modelo nuevo, empezar desde el paso 2.
Si la feature no requiere migración, omitir el paso 7.

## Orden de integración frontend

Para cada página, integrar siempre en este orden:

```
1. Auth guard → 2. Fetch datos → 3. Render → 4. Manejo de errores → 5. Loading state
```

---

## Paso 1 — Model (SQLAlchemy 2.0)

Usar siempre `Mapped` y `mapped_column`. Nunca `Column()` legacy.

```python
# backend/models/notification_model.py
import uuid
from datetime import datetime, timezone
from sqlalchemy import Text, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.database import Base

class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    request_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("requests.id"), nullable=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc), nullable=False
    )

    user: Mapped["User"] = relationship("User", foreign_keys=[user_id], back_populates="notifications")
    request: Mapped["Request | None"] = relationship("Request", foreign_keys=[request_id], back_populates="notifications")
```

**Reglas:**
- `datetime` siempre con `lambda: datetime.now(timezone.utc)` — nunca `datetime.utcnow`
- FKs opcionales: `Mapped[uuid.UUID | None]` + `nullable=True`
- Relaciones siempre con `back_populates` (bidireccional)
- Agregar el import en `alembic/env.py` para que Alembic detecte el modelo

---

## Paso 2 — Schema (Pydantic)

```python
# backend/schemas/notification_schema.py
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict

class NotificationOut(BaseModel):
    id: UUID
    user_id: UUID
    request_id: UUID | None
    message: str
    is_read: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class NotificationUpdate(BaseModel):
    is_read: bool
```

**Reglas:**
- Siempre `ConfigDict(from_attributes=True)` en schemas de salida
- Nunca exponer `password_hash`
- Nombre de archivo: `notification_schema.py`, `user_schema.py`, etc.

---

## Paso 3 — Repository

Solo acceso a DB. Sin lógica de negocio, sin HTTP.

```python
# backend/repositories/notification_repository.py
def get_by_user(db: Session, user_id: UUID) -> list[Notification]:
    stmt = (
        select(Notification)
        .where(Notification.user_id == user_id)
        .order_by(Notification.created_at.desc())
    )
    return list(db.execute(stmt).scalars().all())

def create(db: Session, user_id: UUID, message: str, request_id: UUID | None = None) -> Notification:
    try:
        notif = Notification(user_id=user_id, request_id=request_id, message=message)
        db.add(notif)
        db.commit()
        db.refresh(notif)
        return notif
    except Exception:
        db.rollback()
        raise
```

**Reglas:**
- Usar `select()` de SQLAlchemy 2.0, no `db.query()`
- Transacciones atómicas con try/except + rollback
- `db.get(Model, pk)` para búsqueda por PK

---

## Paso 4 — Service

Solo lógica de negocio. Sin HTTP, sin `db.query()`.

```python
def get_my_notifications(db: Session, current_user: User) -> list[Notification]:
    return notification_repository.get_by_user(db, current_user.id)

def mark_notification_read(db: Session, notification_id: UUID, current_user: User) -> Notification:
    notification = notification_repository.mark_as_read(db, notification_id, current_user.id)
    if not notification:
        raise EcoRetiroExceptions.NOTIFICATION_NOT_FOUND
    return notification
```

**Reglas:**
- Excepciones siempre desde `core/exceptions.py`
- Nunca importar `HTTPException` directamente en el service

---

## Paso 5 — Router

Solo HTTP y delegación al service.

```python
router = APIRouter(prefix="/notifications", tags=["notifications"])

@router.get("/me", response_model=list[NotificationOut])
async def get_my_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> list[NotificationOut]:
    return notification_service.get_my_notifications(db, current_user)
```

**Reglas:**
- Auth: `get_current_user` para USER, `require_role("OPERATOR")` para roles elevados
- Nunca `db.query()` en el router
- Registrar el router en `backend/main.py`

---

## Paso 6 — Tests

Siempre con `StaticPool`. Importar todos los modelos en `conftest.py`.

```python
def test_get_my_notifications_returns_200(client: TestClient):
    token = register_and_login(client)
    resp = client.get("/notifications/me", headers=auth_headers(token))
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)

def test_mark_notification_read_from_other_user_returns_404(client: TestClient):
    """Seguridad: user B no puede marcar notif de user A."""
    token_a = register_and_login(client, email="usera@eco.com")
    token_b = register_and_login(client, email="userb@eco.com")

    db = TestingSessionLocal()
    user_a = db.query(User).filter(User.email == "usera@eco.com").first()
    notif = notification_repository.create(db, user_a.id, "Test")
    notif_id = str(notif.id)
    db.close()

    resp = client.patch(f"/notifications/{notif_id}", headers=auth_headers(token_b))
    assert resp.status_code == 404
```

**Reglas:**
- Siempre `StaticPool` + `Base.metadata.create_all` en el fixture `client`
- Todos los modelos importados en `conftest.py` antes de `create_all`
- Cubrir: happy path, auth requerida (401), not found (404), permisos (403)

---

## Paso 7 — Migración Alembic

```bash
alembic revision --autogenerate -m "descripcion_corta"
# Revisar el archivo generado antes de aplicar
alembic upgrade head
```

**Verificar en el archivo generado:**
- `op.create_table(...)` tiene todas las columnas del modelo
- FKs y nullable correctos
- `op.drop_table(...)` en `downgrade()` es reversible

---

## Integración frontend — Patrón base

Cada página protegida sigue este patrón en su `<script>`:

```javascript
(function () {
  'use strict';

  // 1. Auth guard
  if (!EcoRetiroAPI.getToken()) {
    EcoRetiroAPI.redirectToLogin();
    return;
  }

  // 2. Fetch y render
  EcoRetiroAPI.getSomeData()
    .then(function (data) {
      // 3. Render con escapeHtml() para datos del backend
      document.getElementById('element').textContent = escapeHtml(data.field);
    })
    .catch(function (err) {
      // 4. Error state
      showError(err.message);
    });

  function escapeHtml(str) {
    var div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  }
})();
```

---

## api.js — Funciones disponibles

```javascript
EcoRetiroAPI.getToken()
EcoRetiroAPI.setToken(token)
EcoRetiroAPI.clearToken()
EcoRetiroAPI.redirectToLogin()
EcoRetiroAPI.authFetch(endpoint, options)  // Bearer token + maneja 401

EcoRetiroAPI.login(email, password)         // POST /auth/login → guarda token
EcoRetiroAPI.register(name, email, password, phone)  // POST /auth/register → auto-login

EcoRetiroAPI.getCurrentUser()               // GET /users/me
EcoRetiroAPI.getMyRequests()                // GET /requests/me
EcoRetiroAPI.getMyNotifications()           // GET /notifications/me
```

> Agregar nuevas funciones siguiendo el mismo patrón:
> `function nombre() { return authFetch('/endpoint'); }`
> Y exportar en `window.EcoRetiroAPI`.

---

## STATUS_MAP — Estados del backend

```javascript
var STATUS_MAP = {
  REQUESTED:         { label: 'SOLICITADA',   css: '' },
  SCHEDULED:         { label: 'AGENDADA',     css: 'scheduled' },
  IN_ROUTE:          { label: 'EN CAMINO',    css: '' },
  COLLECTED:         { label: 'RECOLECTADA',  css: '' },
  CLASSIFIED:        { label: 'CLASIFICADA',  css: '' },
  RECOVERED:         { label: 'RECUPERADA',   css: '' },
  SENT_TO_RECYCLING: { label: 'EN RECICLAJE', css: 'scheduled' },
  COMPLETED:         { label: 'COMPLETADA',   css: 'completed' }
};
```

CSS classes: sin clase = verde, `scheduled` = amarillo, `completed` = gris.

## TIME_MAP — Horarios del backend

```javascript
var TIME_MAP = {
  MORNING:   'Mañana',
  AFTERNOON: 'Tarde',
  EVENING:   'Noche'
};
```

---

## Convenciones de seguridad frontend

- **XSS:** siempre `escapeHtml()` para datos del backend renderizados en innerHTML
- **Token:** nunca exponer en URLs ni logs
- **401:** siempre `EcoRetiroAPI.redirectToLogin()` — limpia token y redirige
- **Live Server:** siempre puerto 5500, nunca `file://`
- **Imports:** `api.js` antes de `window-system.js` en todos los HTML

---

## Prompts de referencia

**Nueva feature backend:**
```
Following the workflow in docs/ai/ai_workflow.md, implement [feature].
Start with Step [N] — [descripción] in backend/[capa]/[archivo].
Wait for my approval before moving to the next step.
```

**Nueva integración frontend:**
```
@workspace Integrate [page].html with backend API.
#file:/home/estudiante/ecoretiro/frontend/js/api.js
#file:/home/estudiante/ecoretiro/frontend/pages/[page].html

Follow the integration pattern in docs/ai/ai_workflow.md.
Add needed functions to api.js first, show complete file, wait for approval.
Then show complete [page].html with integration script, wait for approval.
```

**Bugfix en capa backend:**
```
This endpoint is failing: [METHOD] [ruta]
Error: [mensaje]
Identify which layer has the problem.
Fix only that layer. Show me the full content of the modified file.
```

**Bugfix en integración frontend:**
```
This fetch is failing: [METHOD] [endpoint]
Error: [mensaje]
Check api.js authFetch wrapper and [page].html script.
Fix only the failing part. Show the complete modified file.
```

**Agregar validación backend:**
```
Add validation to [schema] for [campo]: [reglas].
Validation must be in the Pydantic schema only.
Add a test for the 422 failure case.
```

**Integrar notificación en service existente:**
```
In [service_file], after [evento], call notification_repository.create()
to notify the affected user. Import notification_repository.
Do not modify any other layer. Show me only the modified function.
```
