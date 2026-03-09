"""
tests/test_requests.py — EcoRetiro
Casos: crear solicitud, protección auth, tracking existente y no existente.
"""
from fastapi.testclient import TestClient
from tests.conftest import REQUEST_PAYLOAD, register_and_login, auth_headers, operator_token


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
