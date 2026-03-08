# docs/ai/ai_workflow.md — Flujo de Desarrollo con Ejemplos

## Orden de implementación por capa

Para cada feature nueva, implementar en este orden:

```
1. model → 2. schema → 3. repository → 4. service → 5. router → 6. tests → 7. migration
```

---

## Paso 1 — Model (SQLAlchemy)

```python
# backend/models/request.py
import uuid
from sqlalchemy import Column, String, Date, Float, ForeignKey, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from backend.database import Base
from backend.models.enums import RequestStatus, MaterialType, EstimatedVolume, VehicleType

class Request(Base):
    __tablename__ = "requests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tracking_number = Column(String(30), unique=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    address = Column(String, nullable=False)
    description = Column(String, nullable=False)
    material_type = Column(SAEnum(MaterialType), nullable=False)
    estimated_volume = Column(SAEnum(EstimatedVolume), nullable=False)
    current_status = Column(SAEnum(RequestStatus), default=RequestStatus.REQUESTED)
    # ... resto de campos
```

---

## Paso 2 — Schema (Pydantic)

```python
# backend/schemas/request.py
from pydantic import BaseModel, ConfigDict, field_validator
from datetime import date
from uuid import UUID

class RequestCreate(BaseModel):
    address: str
    description: str
    material_type: str
    estimated_volume: str
    pickup_date: date
    pickup_time_range: str

    @field_validator("pickup_date")
    @classmethod
    def date_not_past(cls, v: date) -> date:
        if v < date.today():
            raise ValueError("La fecha no puede ser en el pasado")
        return v

class RequestRead(BaseModel):
    id: UUID
    tracking_number: str
    current_status: str
    material_type: str
    pickup_date: date
    model_config = ConfigDict(from_attributes=True)
    # password_hash nunca aparece acá
```

---

## Paso 3 — Repository

```python
# backend/repositories/request_repository.py
from sqlalchemy.orm import Session
from sqlalchemy import extract
from datetime import datetime
from uuid import UUID
from backend.models.request import Request
from backend.schemas.request import RequestCreate

def get_by_id(db: Session, request_id: UUID) -> Request | None:
    return db.query(Request).filter(Request.id == request_id).first()

def get_by_tracking_number(db: Session, tracking_number: str) -> Request | None:
    return db.query(Request).filter(
        Request.tracking_number == tracking_number
    ).first()

def generate_tracking_number(db: Session) -> str:
    year = datetime.now().year
    count = db.query(Request).filter(
        extract("year", Request.created_at) == year
    ).count()
    return f"ECO-USHUAIA-{year}-{str(count + 1).zfill(5)}"

def create_with_history(db: Session, data: RequestCreate, user_id: UUID) -> Request:
    # transacción atómica: request + status inicial
    try:
        tracking = generate_tracking_number(db)
        new_request = Request(**data.model_dump(), user_id=user_id, tracking_number=tracking)
        db.add(new_request)
        db.flush()  # obtiene ID sin commit

        from backend.models.status_history import StatusHistory
        from backend.models.enums import RequestStatus
        history = StatusHistory(
            request_id=new_request.id,
            status=RequestStatus.REQUESTED,
            updated_by=user_id
        )
        db.add(history)
        db.commit()
        db.refresh(new_request)
        return new_request
    except Exception:
        db.rollback()
        raise
```

---

## Paso 4 — Service

```python
# backend/services/request_service.py
from sqlalchemy.orm import Session
from uuid import UUID
from backend.repositories import request_repository
from backend.schemas.request import RequestCreate, RequestRead
from backend.models.request import Request
from backend.core.exceptions import EcoRetiroExceptions

def create(db: Session, data: RequestCreate, user_id: UUID) -> Request:
    # lógica de negocio pura, sin db.query()
    return request_repository.create_with_history(db, data, user_id)

def get_or_404(db: Session, request_id: UUID) -> Request:
    request = request_repository.get_by_id(db, request_id)
    if not request:
        raise EcoRetiroExceptions.REQUEST_NOT_FOUND
    return request
```

---

## Paso 5 — Router

```python
# backend/routers/requests.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from uuid import UUID
from backend.core.dependencies import get_db, get_current_user
from backend.models.user import User
from backend.schemas.request import RequestCreate, RequestRead
from backend.services import request_service

router = APIRouter(prefix="/requests", tags=["requests"])

@router.post("", response_model=RequestRead, status_code=201)
async def create_request(
    data: RequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> RequestRead:
    # router es thin: solo HTTP + delegación
    return request_service.create(db, data, current_user.id)
```

---

## Paso 6 — Tests

```python
# tests/test_requests.py
def test_create_request_returns_tracking_number(client, auth_token):
    response = client.post(
        "/requests",
        json={
            "address": "San Martín 123, Ushuaia",
            "description": "PC vieja y cables",
            "material_type": "COMPUTADORA",
            "estimated_volume": "SMALL",
            "pickup_date": "2027-01-15",
            "pickup_time_range": "MORNING"
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 201
    data = response.json()
    assert "tracking_number" in data
    assert data["tracking_number"].startswith("ECO-USHUAIA-")

def test_create_request_requires_auth(client):
    response = client.post("/requests", json={})
    assert response.status_code == 401

def test_create_request_past_date_fails(client, auth_token):
    response = client.post(
        "/requests",
        json={"pickup_date": "2020-01-01", ...},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 422
```

---

## Paso 7 — Migración Alembic

```bash
# Generar migración automática desde los modelos
alembic revision --autogenerate -m "agrega tabla requests"

# Revisar el archivo generado en alembic/versions/
# Aplicar la migración
alembic upgrade head
```
