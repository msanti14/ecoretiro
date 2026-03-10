"""
tests/test_requests.py — EcoRetiro
Casos: crear solicitud, protección auth, tracking existente y no existente.
Tests de integración con notificaciones automáticas.
"""
from fastapi.testclient import TestClient
from tests.conftest import REQUEST_PAYLOAD, register_and_login, auth_headers, operator_token
from backend.models.notification_model import Notification
from tests.conftest import TestingSessionLocal


# ── Crear solicitud ───────────────────────────────────────────────────────────

def test_create_request_returns_tracking_number(client: TestClient):
    token = register_and_login(client)

    resp = client.post(
        "/requests",
        json=REQUEST_PAYLOAD,
        headers=auth_headers(token),
    )

    assert resp.status_code == 201
    body = resp.json()
    assert "tracking_number" in body
    assert body["tracking_number"].startswith("ECO-USHUAIA-")  # ECO-USHUAIA-{AÑO}-{SEQ}
    assert body["current_status"] == "REQUESTED"


def test_create_request_requires_auth_returns_401(client: TestClient):
    resp = client.post("/requests", json=REQUEST_PAYLOAD)   # sin token

    # Sin token el header Authorization falta → FastAPI devuelve 401 o 422
    # según cómo esté implementado get_current_user_id en core/dependencies.py
    assert resp.status_code in (401, 422)


# ── Tracking público ──────────────────────────────────────────────────────────

def test_track_existing_request_returns_200(client: TestClient):
    # Crear solicitud para obtener un tracking_number real
    token = register_and_login(client)
    create_resp = client.post(
        "/requests",
        json=REQUEST_PAYLOAD,
        headers=auth_headers(token),
    )
    tracking_number = create_resp.json()["tracking_number"]

    resp = client.get(f"/track/{tracking_number}")   # endpoint público, sin token

    assert resp.status_code == 200
    body = resp.json()
    assert body["tracking_number"] == tracking_number
    assert body["current_status"] == "REQUESTED"
    assert isinstance(body["history"], list)
    assert len(body["history"]) >= 1                 # al menos el estado inicial


def test_track_nonexistent_returns_404(client: TestClient):
    resp = client.get("/track/ECO-NOEXISTE-9999")

    assert resp.status_code == 404


# ── GET /requests (OPERATOR/ADMIN only) ────────────────────────────────────────

def test_list_all_requests_as_operator_returns_200(client: TestClient, operator_token: str):
    resp = client.get("/requests", headers=auth_headers(operator_token))

    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_list_all_requests_as_user_returns_403(client: TestClient):
    token = register_and_login(client)

    resp = client.get("/requests", headers=auth_headers(token))

    assert resp.status_code == 403


# ── Integración con notificaciones automáticas ────────────────────────────────

def test_create_request_creates_notification(client: TestClient):
    """Verificar que al crear una solicitud se dispara automáticamente una notificación."""
    token = register_and_login(client, email="user_notif@eco.com")

    # Crear solicitud
    resp = client.post(
        "/requests",
        json=REQUEST_PAYLOAD,
        headers=auth_headers(token),
    )
    
    assert resp.status_code == 201
    tracking_number = resp.json()["tracking_number"]

    # Verificar que se creó una notificación en la DB
    db = TestingSessionLocal()
    try:
        notifications = db.query(Notification).all()
        assert len(notifications) == 1
        
        notification = notifications[0]
        assert f"Tu solicitud {tracking_number} fue recibida." in notification.message
        assert notification.is_read is False
    finally:
        db.close()


def test_update_status_creates_notification(client: TestClient, operator_token: str):
    """Verificar que al cambiar el estado se dispara automáticamente una notificación."""
    # Usuario crea solicitud
    user_token = register_and_login(client, email="user_status@eco.com")
    create_resp = client.post(
        "/requests",
        json=REQUEST_PAYLOAD,
        headers=auth_headers(user_token),
    )
    request_id = create_resp.json()["id"]
    tracking_number = create_resp.json()["tracking_number"]

    # Operador cambia el estado a SCHEDULED
    update_resp = client.patch(
        f"/requests/{request_id}/status",
        json={"current_status": "SCHEDULED"},
        headers=auth_headers(operator_token),
    )
    
    assert update_resp.status_code == 200

    # Verificar que hay 2 notificaciones: 1 al crear + 1 al cambiar estado
    db = TestingSessionLocal()
    try:
        notifications = db.query(Notification).order_by(Notification.created_at).all()
        assert len(notifications) == 2
        
        # Primera notificación (creación)
        assert f"Tu solicitud {tracking_number} fue recibida." in notifications[0].message
        
        # Segunda notificación (cambio de estado)
        assert f"Tu solicitud {tracking_number} cambió a agendada." in notifications[1].message
    finally:
        db.close()


def test_update_vehicle_only_does_not_create_notification(client: TestClient, operator_token: str):
    """Verificar que actualizar solo vehicle_assigned NO dispara notificación."""
    # Usuario crea solicitud
    user_token = register_and_login(client, email="user_vehicle@eco.com")
    create_resp = client.post(
        "/requests",
        json=REQUEST_PAYLOAD,
        headers=auth_headers(user_token),
    )
    request_id = create_resp.json()["id"]

    # Operador solo asigna vehículo (sin cambiar estado)
    update_resp = client.patch(
        f"/requests/{request_id}/status",
        json={"vehicle_assigned": "DUCATO"},  # Solo vehículo, sin current_status
        headers=auth_headers(operator_token),
    )
    
    assert update_resp.status_code == 200

    # Verificar que solo hay 1 notificación (la de creación)
    db = TestingSessionLocal()
    try:
        notifications = db.query(Notification).all()
        assert len(notifications) == 1
        assert "fue recibida" in notifications[0].message
    finally:
        db.close()
