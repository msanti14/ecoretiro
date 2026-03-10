"""
tests/test_notifications.py — EcoRetiro
Casos: listar notificaciones, marcar como leída, protección auth, 404.
"""
from fastapi.testclient import TestClient
from tests.conftest import register_and_login, auth_headers


# ── GET /notifications/me ─────────────────────────────────────────────────────
def test_get_my_notifications_returns_200(client: TestClient):
    token = register_and_login(client)
    resp = client.get("/notifications/me", headers=auth_headers(token))
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body, list)
    # Usuario nuevo no tiene notificaciones
    assert len(body) == 0


def test_get_my_notifications_requires_auth_returns_401(client: TestClient):
    resp = client.get("/notifications/me")
    assert resp.status_code in (401, 422)


# ── PATCH /notifications/{id} ─────────────────────────────────────────────────
def test_mark_notification_read_requires_auth_returns_401(client: TestClient):
    resp = client.patch("/notifications/12345678-1234-1234-1234-123456789012", json={"is_read": True})
    assert resp.status_code in (401, 422)


def test_mark_notification_read_not_found_returns_404(client: TestClient):
    token = register_and_login(client)
    fake_id = "12345678-1234-1234-1234-123456789012"
    resp = client.patch(
        f"/notifications/{fake_id}",
        json={"is_read": True},
        headers=auth_headers(token)
    )
    assert resp.status_code == 404


def test_mark_notification_read_from_other_user_returns_404(client: TestClient):
    """User B cannot mark as read a notification that belongs to User A."""
    from backend.repositories import notification_repository
    from backend.models.user_model import User
    from tests.conftest import TestingSessionLocal

    token_a = register_and_login(client, email="usera@eco.com")
    token_b = register_and_login(client, email="userb@eco.com")

    db = TestingSessionLocal()
    user_a = db.query(User).filter(User.email == "usera@eco.com").first()
    notif = notification_repository.create(db, user_a.id, "Test notification")
    notif_id = str(notif.id)
    db.close()

    resp = client.patch(f"/notifications/{notif_id}", headers=auth_headers(token_b))
    assert resp.status_code == 404