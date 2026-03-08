# docs/ai/ai_prompts.md — Prompts de Uso Rápido

## Implementar una feature nueva

```
Following the workflow in AI_RULES.md, implement [feature].

Follow this order and show me one layer at a time:
1. model
2. schema
3. repository
4. service
5. router
6. tests
7. migration

Wait for my approval before moving to the next layer.
Reference ARCHITECTURE.md for conventions.
```

---

## Revisar código existente

```
Review [ruta del archivo] against AI_RULES.md.

Check for:
- Layer violations (router→repository, service→db.query)
- Missing type hints
- Inline HTTPExceptions instead of core/exceptions.py
- password_hash exposed in response schemas
- Missing tests for this endpoint
- Non-atomic multi-write operations

Report all issues found before suggesting fixes.
```

---

## Crear migración

```
I modified [nombre del modelo] by [descripción del cambio].

Generate the correct Alembic migration and verify:
- The migration matches the model change exactly
- No existing data will be lost
- Required indexes are included
- The migration is reversible (downgrade works)
```

---

## Debuggear un error

```
This endpoint is failing: [método] [ruta]
Error: [mensaje de error]
Stack trace: [si existe]

Check against ARCHITECTURE.md and AI_RULES.md.
Identify which layer contains the problem.
Fix only that layer without touching others.
```

---

## Agregar validación

```
Add validation to [schema/endpoint] for [campo]:
- [regla 1]
- [regla 2]

Validation must be in the Pydantic schema, not in the router or service.
Use field_validator following the pattern in docs/ai/ai_architecture.md.
Add a test for the validation failure case (422).
```

---

## Agregar un test

```
Write tests for [endpoint o función].

Cover:
- Happy path (200/201)
- Not found (404) if applicable
- Forbidden (403) if auth required
- Validation error (422)

Follow the fixture pattern in docs/ai/ai_architecture.md.
Use descriptive test names.
```

---

## Revisar seguridad de un endpoint

```
Security review for [ruta del archivo o endpoint].

Check:
1. Is authentication required and implemented?
2. Is role authorization correct for USER/OPERATOR/ADMIN?
3. Is password_hash absent from all response schemas?
4. Are all inputs validated via Pydantic?
5. Are error messages safe (no internal details exposed)?

Report findings before making changes.
```
