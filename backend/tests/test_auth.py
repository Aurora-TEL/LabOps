import asyncio

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.core.security import require_permissions, require_roles
from app.main import app
from app.schemas.auth import CurrentUser

client = TestClient(app)


def data(response):
    assert response.json()["code"] == 0
    return response.json()["data"]


def test_login_success_returns_jwt_and_user() -> None:
    response = client.post("/api/v1/auth/login", json={"username": "admin", "password": "labops123"})

    payload = data(response)
    assert response.status_code == 200
    assert payload["token_type"] == "bearer"
    assert payload["access_token"] != "placeholder.jwt.token"
    assert payload["expires_in"] > 0
    assert payload["user"]["username"] == "admin"
    assert "system_admin" in payload["user"]["roles"]
    assert "role:manage" in payload["user"]["permissions"]


def test_login_failure_uses_api_response_shape() -> None:
    response = client.post("/api/v1/auth/login", json={"username": "admin", "password": "wrong"})

    assert response.status_code == 401
    assert response.json() == {"code": 40001, "message": "invalid username or password", "data": None}


def test_me_returns_user_from_bearer_token() -> None:
    login_response = client.post("/api/v1/auth/login", json={"username": "student01", "password": "labops123"})
    token = data(login_response)["access_token"]

    response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})

    payload = data(response)
    assert response.status_code == 200
    assert payload["username"] == "student01"
    assert payload["roles"] == ["student"]
    assert "reservation:create" in payload["permissions"]


def test_me_rejects_missing_token() -> None:
    response = client.get("/api/v1/auth/me")

    assert response.status_code == 401
    assert response.json()["code"] == 40001
    assert response.json()["message"] == "invalid or missing authentication token"


def test_require_roles_and_permissions_helpers() -> None:
    user = CurrentUser(
        id="00000000-0000-0000-0000-000000000001",
        username="manager",
        real_name="Manager",
        roles=["lab_admin"],
        permissions=["device:update"],
    )

    assert asyncio.run(require_roles("lab_admin")(user)) == user
    assert asyncio.run(require_permissions("device:update")(user)) == user

    with pytest.raises(HTTPException) as role_error:
        asyncio.run(require_roles("system_admin")(user))
    assert role_error.value.status_code == 403

    with pytest.raises(HTTPException) as permission_error:
        asyncio.run(require_permissions("role:manage")(user))
    assert permission_error.value.status_code == 403
