# docs/ai/ai_architecture.md — Cheatsheet de Arquitectura

## Patrón de Dependencias en Routers

```python
@router.get("/{id}", response_model=EntityRead)
async def get_entity(
    entity_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> EntityRead:
    return entity_service.get_or_404(db, entity_id)
```

---

## Patrón de Repository

```python
# repositories/<entity>_repository.py

def get_by_id(db: Session, entity_id: UUID) -> Entity | None: ...
def get_all(db: Session, skip: int = 0, limit: int = 100) -> list[Entity]: ...
def create(db: Session, data: EntityCreate) -> Entity: ...
def update(db: Session, entity_id: UUID, data: EntityUpdate) -> Entity | None: ...
def delete(db: Session, entity_id: UUID) -> bool: ...
```

---

## Patrón de Service

```python
# services/<entity>_service.py

def get_or_404(db: Session, entity_id: UUID) -> Entity:
    entity = entity_repository.get_by_id(db, entity_id)
    if not entity:
        raise EcoRetiroExceptions.ENTITY_NOT_FOUND
    return entity

def create(db: Session, data: EntityCreate, user_id: UUID) -> Entity:
    # validaciones de negocio acá
    return entity_repository.create(db, data)
```

---

## Patrón de Excepción

```python
# core/exceptions.py

class EcoRetiroExceptions:
    REQUEST_NOT_FOUND = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Solicitud no encontrada"
    )
    NOT_ENOUGH_PERMISSIONS = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="No tenés permisos para esta acción"
    )
    INVALID_STATUS_TRANSITION = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Transición de estado no permitida"
    )
```

---

## Patrón de Transacción Atómica

```python
def create_with_related(db: Session, data: ...) -> Model:
    try:
        main = MainModel(**data)
        db.add(main)
        db.flush()           # ID disponible sin commit

        related = RelatedModel(main_id=main.id, ...)
        db.add(related)

        db.commit()
        db.refresh(main)
        return main
    except Exception:
        db.rollback()
        raise
```

---

## Patrón de Validación de Estado

```python
# services/tracking_service.py

ALLOWED_TRANSITIONS: dict[RequestStatus, list[RequestStatus]] = {
    RequestStatus.REQUESTED:         [RequestStatus.SCHEDULED],
    RequestStatus.SCHEDULED:         [RequestStatus.IN_ROUTE],
    RequestStatus.IN_ROUTE:          [RequestStatus.COLLECTED],
    RequestStatus.COLLECTED:         [RequestStatus.CLASSIFIED],
    RequestStatus.CLASSIFIED:        [RequestStatus.RECOVERED, RequestStatus.SENT_TO_RECYCLING],
    RequestStatus.RECOVERED:         [RequestStatus.COMPLETED],
    RequestStatus.SENT_TO_RECYCLING: [RequestStatus.COMPLETED],
    RequestStatus.COMPLETED:         [],
}

def validate_transition(current: RequestStatus, new: RequestStatus) -> bool:
    return new in ALLOWED_TRANSITIONS.get(current, [])
```

---

## Patrón de Protección por Rol

```python
# core/dependencies.py

def require_role(*roles: UserRole):
    def dependency(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise EcoRetiroExceptions.NOT_ENOUGH_PERMISSIONS
        return current_user
    return dependency

# Uso en router:
@router.patch("/{id}/status")
async def update_status(
    ...,
    current_user: User = Depends(require_role(UserRole.OPERATOR, UserRole.ADMIN))
): ...
```

---

## Fixture de Tests (conftest.py)

```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.main import app
from backend.database import Base, get_db

engine = create_engine("sqlite:///./test.db", connect_args={"check_same_thread": False})
TestingSession = sessionmaker(bind=engine)

@pytest.fixture
def client():
    Base.metadata.create_all(bind=engine)
    def override():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()
    app.dependency_overrides[get_db] = override
    yield TestClient(app)
    Base.metadata.drop_all(bind=engine)
```
