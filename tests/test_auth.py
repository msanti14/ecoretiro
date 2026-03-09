"""
tests/test_auth.py — EcoRetiro
Casos: registro, email duplicado, login válido, contraseña inválida.
"""
from fastapi.testclient import TestClient
from tests.conftest import REGISTER_URL, LOGIN_URL, USER_DATA


# ── Registro ──────────────────────────────────────────────────────────────────

def test_register_user_returns_201(client: TestClient):
    resp = client.post(REGISTER_URL, json=USER_DATA)

    assert resp.status_code == 201
    body = resp.json()
    assert body["email"] == USER_DATA["email"]
    assert body["name"] == USER_DATA["name"]
    assert "id" in body
    assert "password_hash" not in body          # nunca se expone


def test_register_duplicate_email_returns_409(client: TestClient):
    client.post(REGISTER_URL, json=USER_DATA)   # primer registro

    resp = client.post(REGISTER_URL, json=USER_DATA)   # mismo email

    assert resp.status_code == 409


# ── Login ─────────────────────────────────────────────────────────────────────

def test_login_valid_credentials_returns_token(client: TestClient):
    client.post(REGISTER_URL, json=USER_DATA)

    resp = client.post(LOGIN_URL, json={
        "email": USER_DATA["email"],
        "password": USER_DATA["password"],
    })

    assert resp.status_code == 200
    body = resp.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"


def test_login_invalid_password_returns_401(client: TestClient):
    client.post(REGISTER_URL, json=USER_DATA)

    resp = client.post(LOGIN_URL, json={
        "email": USER_DATA["email"],
        "password": "wrongpassword9",
    })

    assert resp.status_code == 401
