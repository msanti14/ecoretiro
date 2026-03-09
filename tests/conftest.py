"""
tests/conftest.py — EcoRetiro
SQLite in-memory con StaticPool: una sola conexión, tablas persistentes en el test.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.main import app
from backend.database import Base
from backend.core.dependencies import get_db

# ── Importar modelos para que Base.metadata los registre antes de create_all ──
from backend.models.user_model import User, UserRole              # noqa: F401
from backend.models.request_model import Request                # noqa: F401
from backend.models.status_history_model import StatusHistory   # noqa: F401

# ── StaticPool: reutiliza una sola conexión → la DB in-memory no desaparece ──
engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


# ── Fixture principal ─────────────────────────────────────────────────────────
@pytest.fixture
def client():
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)

    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()


# ── Helpers reutilizables ─────────────────────────────────────────────────────
REGISTER_URL = "/auth/register"
LOGIN_URL    = "/auth/login"

USER_DATA = {
    "name": "Test User",
    "email": "test@eco.com",
    "password": "Secret123!",
}

def register_and_login(client: TestClient, email: str = "test@eco.com") -> str:
    """Registra un usuario y devuelve el Bearer token."""
    client.post(REGISTER_URL, json={**USER_DATA, "email": email})
    resp = client.post(LOGIN_URL, json={"email": email, "password": "Secret123!"})
    return resp.json()["access_token"]


def auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def operator_token(client: TestClient) -> str:
    """Registra un usuario, actualiza su rol a OPERATOR en DB y devuelve el token."""
    email = "operator@eco.com"
    client.post(REGISTER_URL, json={**USER_DATA, "email": email})
    db = TestingSessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        user.role = UserRole.OPERATOR
        db.commit()
    finally:
        db.close()
    resp = client.post(LOGIN_URL, json={"email": email, "password": USER_DATA["password"]})
    return resp.json()["access_token"]


# Fecha futura fija para evitar el validator pickup_date_not_past
REQUEST_PAYLOAD = {
    "address": "Av. Corrientes 1234, CABA",
    "description": "Computadora vieja para reciclar",
    "material_type": "COMPUTADORA",
    "estimated_volume": "SMALL",
    "pickup_date": "2099-12-01",
    "pickup_time_range": "MORNING",
}
