# AI_RULES.md — EcoRetiro
# Reglas operativas para la IA que trabaja en este proyecto

---

## Fuentes de Verdad

Antes de escribir cualquier código, leer en este orden:

1. `PROJECT.md` — contexto general del proyecto
2. `ARCHITECTURE.md` — estructura, capas, modelos, endpoints
3. `AI_RULES.md` — este archivo, reglas operativas
4. `AI_PROJECT_PROMPT.md` — prompt maestro

---

## Flujo de Desarrollo Obligatorio

Para cada nueva feature, seguir SIEMPRE este orden. No saltear pasos.

```
1. model         → backend/models/<entidad>.py
2. schema        → backend/schemas/<entidad>.py
3. repository    → backend/repositories/<entidad>_repository.py
4. service       → backend/services/<entidad>_service.py
5. router        → backend/routers/<entidad>.py
6. tests         → tests/test_<entidad>.py
7. migration     → alembic revision --autogenerate -m "descripción"
```

Si el paso anterior no existe, no avanzar al siguiente.

---

## Reglas de Arquitectura

### Flujo obligatorio
```
router → service → repository → db
```

### Lo que NUNCA puede pasar

| Violación | Ejemplo prohibido |
|-----------|------------------|
| Router accede a DB | `db.query()` en `routers/` |
| Service accede a DB directo | `db.query()` en `services/` |
| Router llama a repository | `user_repository.get()` en `routers/` |
| Lógica de negocio en router | Validaciones de estado en `routers/` |
| Schema importa modelo | `from backend.models import User` en `schemas/` |

Si detectás una violación en el código existente, reportala antes de continuar.

---

## Reglas de Código Python

- Type hints **obligatorios** en TODAS las funciones y métodos
- PEP8 estricto
- Nombres en inglés. Comentarios en español.
- Primary keys: UUID siempre, nunca integers
- Sin `print()` de debug
- Sin logging excesivo en MVP

```python
# Correcto
async def get_by_tracking(tracking_number: str, db: Session) -> Request | None:
    # Retorna None si no existe; el router maneja el 404
    return db.query(Request).filter(
        Request.tracking_number == tracking_number
    ).first()

# Incorrecto
def get_by_tracking(tracking_number, db):  # ❌ sin type hints
    return db.query(Request).filter(...)
```

---

## Reglas de Schemas Pydantic

- `Create` → entrada del usuario (POST body)
- `Read` → respuesta al usuario
- `Update` → actualización parcial (PATCH)
- `Read` siempre incluye `model_config = ConfigDict(from_attributes=True)`
- **NUNCA** incluir `password_hash` en ningún schema `Read`

```python
class UserRead(BaseModel):
    id: UUID
    name: str
    email: str
    role: UserRole
    # password_hash ausente siempre ←
    model_config = ConfigDict(from_attributes=True)
```

---

## Reglas de Validación

Toda validación de entrada va en schemas Pydantic, nunca en routers ni services.

| Campo | Validación |
|-------|-----------|
| `email` | `EmailStr` de pydantic |
| `password` | Mínimo 8 chars, al menos 1 número |
| `phone` | Solo dígitos, 7-15 chars, opcional |
| `name` | Min 2 chars, max 100 |
| `pickup_date` | No puede ser fecha pasada |
| `description` | Min 10 chars, max 500 |
| `lat` | Entre -90 y 90 |
| `lng` | Entre -180 y 180 |

---

## Reglas de Manejo de Errores

Los HTTPExceptions reutilizables viven en `core/exceptions.py`.
No crear HTTPExceptions inline en routers.

```python
# Correcto
from backend.core.exceptions import EcoRetiroExceptions
raise EcoRetiroExceptions.REQUEST_NOT_FOUND

# Incorrecto
raise HTTPException(status_code=404, detail="...")  # ❌
```

Estructura estándar de respuesta de error:
```json
{"detail": "Mensaje legible para el usuario"}
```

---

## Reglas de Seguridad

- Rutas OPERATOR y ADMIN: validación de rol via JWT **obligatoria**
- Nunca exponer `password_hash` en ninguna respuesta
- Nunca exponer tokens JWT en logs
- El archivo `.env` no debe ser creado ni modificado por la IA
- `entorno/` y `.env` siempre en `.gitignore`
- CORS configurado en `main.py` para orígenes específicos
- Rate limiting en `/auth/login` (no implementar sin consultar)

---

## Reglas de Transacciones

Operaciones con múltiples escrituras **deben ser atómicas**.

### Crear solicitud — siempre 3 operaciones en 1 transacción
1. Crear registro en `requests`
2. Insertar estado `REQUESTED` en `status_history`
3. Asignar vehículo automáticamente

### Cambiar estado — siempre 2 operaciones en 1 transacción
1. Actualizar `current_status` en `requests`
2. Insertar registro en `status_history`

```python
try:
    db.add(...)
    db.flush()   # obtener ID sin commit
    db.add(...)
    db.commit()
except Exception:
    db.rollback()
    raise
```

---

## Reglas de Estados

- Los estados son **unidireccionales**. Nunca retroceder.
- Toda transición se valida con `ALLOWED_TRANSITIONS` en `tracking_service.py`
- Todo cambio se registra en `StatusHistory`

---

## Reglas de Testing

- DB de tests: SQLite en memoria, nunca PostgreSQL de desarrollo
- Cada test crea y destruye sus propios datos (fixtures)
- Nombrar descriptivamente: `test_create_request_returns_tracking_number`
- Cobertura mínima por endpoint:
  - caso feliz (200/201)
  - recurso no encontrado (404)
  - sin permisos (403)
  - datos inválidos (422)
- Nunca mockear la DB en tests de integración

---

## Convención de Nombres de Archivos

| Tipo | Patrón |
|------|--------|
| Modelo | `<entidad>.py` |
| Schema | `<entidad>.py` |
| Repository | `<entidad>_repository.py` |
| Service | `<entidad>_service.py` |
| Router | `<entidad>.py` |
| Test | `test_<entidad>.py` |

---

## Comportamiento ante Ambigüedad

Cuando una instrucción no esté clara o haya más de una forma válida:

1. No asumir. No elegir.
2. Presentar exactamente **2 opciones** con pro/contra en 2-3 líneas.
3. Esperar decisión antes de escribir código.

```
Opción A — [nombre corto]
→ [descripción + ventaja + desventaja]

Opción B — [nombre corto]
→ [descripción + ventaja + desventaja]

¿Cuál preferís?
```

---

## Prohibiciones Absolutas

- Cambiar el stack sin pedido explícito
- Agregar librerías fuera del stack sin avisar
- Crear archivos fuera de la estructura acordada sin avisar
- Funciones Python sin type hints
- `db.query()` dentro de `services/`
- Integers como primary keys
- Retroceder estados
- Exponer `password_hash`
- HTTPExceptions inline en routers
- React, Vue, Angular en el MVP

---

## Contexto del Desarrollador

El desarrollador está aprendiendo Python y FastAPI en paralelo.

- Priorizar claridad sobre optimización prematura
- Elegir siempre la solución más simple
- Avisar si existe una versión más avanzada para cuando escale
- Comentar en español las decisiones de arquitectura no obvias
