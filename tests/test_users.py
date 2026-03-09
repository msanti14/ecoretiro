"""
tests/test_users.py — EcoRetiro
Casos: obtener perfil, actualizar perfil, protección auth.
"""
from fastapi.testclient import TestClient
from tests.conftest import register_and_login, auth_headers, USER_DATA

# ── GET /users/me ─────────────────────────────────────────────────────────────
def test_get_me_returns_200(client: TestClient):
    token = register_and_login(client)
    resp = client.get("/users/me", headers=auth_headers(token))
    assert resp.status_code == 200
    body = resp.json()
    assert body["email"] == USER_DATA["email"]
    assert body["name"] == USER_DATA["name"]
    assert "id" in body
    assert "password_hash" not in body

def test_get_me_requires_auth_returns_401(client: TestClient):
    resp = client.get("/users/me")
    assert resp.status_code in (401, 422)

# ── PATCH /users/me ───────────────────────────────────────────────────────────
def test_patch_me_updates_name_returns_200(client: TestClient):
    token = register_and_login(client)
    resp = client.patch(
        "/users/me",
        json={"name": "Updated Name"},
        headers=auth_headers(token),
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["name"] == "Updated Name"
    assert body["email"] == USER_DATA["email"]

def test_patch_me_wrong_current_password_returns_401(client: TestClient):
    token = register_and_login(client)
    resp = client.patch(
        "/users/me",
        json={
            "password": "NewPassword123!",
            "current_password": "WrongPassword123!",
        },
        headers=auth_headers(token),
    )
    assert resp.status_code == 401

def test_patch_me_requires_auth_returns_401(client: TestClient):
    resp = client.patch("/users/me", json={"name": "New Name"})
    assert resp.status_code in (401, 422)