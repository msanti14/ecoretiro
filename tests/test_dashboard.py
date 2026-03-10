"""
tests/test_dashboard.py — EcoRetiro
Casos: acceso a estadísticas del dashboard ADMIN.
"""
from fastapi.testclient import TestClient
from backend.schemas.dashboard_schema import DashboardStats
from tests.conftest import (
    register_and_login,
    auth_headers,
)


def test_get_stats_as_admin_returns_200_and_structure(
    client: TestClient, admin_token: str
):
    resp = client.get(
        "/admin/stats", headers=auth_headers(admin_token)
    )

    assert resp.status_code == 200
    body = resp.json()
    # should conform to DashboardStats schema
    DashboardStats(**body)

    # sanity checks on types
    assert isinstance(body["total_requests"], int)
    assert isinstance(body["requests_by_status"], dict)
    # values inside requests_by_status must be ints if any
    for v in body["requests_by_status"].values():
        assert isinstance(v, int)
    assert isinstance(body["total_users"], int)
    assert isinstance(body["unread_notifications"], int)


def test_get_stats_requires_auth_returns_401(client: TestClient):
    resp = client.get("/admin/stats")
    assert resp.status_code in (401, 422)


def test_get_stats_as_user_returns_403(client: TestClient):
    token = register_and_login(client)
    resp = client.get(
        "/admin/stats", headers=auth_headers(token)
    )
    assert resp.status_code == 403
