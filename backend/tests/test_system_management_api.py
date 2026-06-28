from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def data(response):
    assert response.json()["code"] == 0
    return response.json()["data"]


def auth_headers(username: str = "admin", password: str = "labops123") -> dict[str, str]:
    response = client.post("/api/v1/auth/login", json={"username": username, "password": password})
    token = data(response)["access_token"]
    return {"Authorization": f"Bearer {token}"}


def find_user(username: str) -> dict:
    payload = data(
        client.get(
            "/api/v1/system/users",
            params={"keyword": username, "page_size": 10},
            headers=auth_headers("admin"),
        )
    )
    matches = [item for item in payload["items"] if item["username"] == username]
    assert matches
    return matches[0]


def test_system_management_summary_roles_and_permissions() -> None:
    summary = data(client.get("/api/v1/system/summary", headers=auth_headers("admin")))
    assert summary["user_total"] >= 6
    assert summary["role_total"] >= 6
    assert summary["permission_total"] >= 20

    roles = data(client.get("/api/v1/system/roles", headers=auth_headers("admin")))
    role_codes = {role["code"] for role in roles}
    assert {"ordinary_user", "device_owner", "system_admin"}.issubset(role_codes)
    assert any("reservation:create" in {permission["code"] for permission in role["permissions"]} for role in roles)

    permissions = data(client.get("/api/v1/system/permissions", headers=auth_headers("admin")))
    assert {"user:manage", "role:manage", "audit_log:view"}.issubset({item["code"] for item in permissions})


def test_system_management_rejects_non_admin_user() -> None:
    assert client.get("/api/v1/system/users", headers=auth_headers("ordinary01")).status_code == 403
    assert client.get("/api/v1/system/roles", headers=auth_headers("owner01")).status_code == 403


def test_update_user_status_and_roles_then_restore() -> None:
    user = find_user("teacher01")
    teacher_token = data(client.post("/api/v1/auth/login", json={"username": "teacher01", "password": "labops123"}))[
        "access_token"
    ]

    disabled = data(
        client.patch(
            f"/api/v1/system/users/{user['id']}/status",
            json={"status": "disabled"},
            headers=auth_headers("admin"),
        )
    )
    assert disabled["status"] == "disabled"
    assert client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {teacher_token}"}).status_code == 403
    assert client.post("/api/v1/auth/login", json={"username": "teacher01", "password": "labops123"}).status_code == 403

    restored = data(
        client.patch(
            f"/api/v1/system/users/{user['id']}/status",
            json={"status": "active"},
            headers=auth_headers("admin"),
        )
    )
    assert restored["status"] == "active"

    updated_roles = data(
        client.put(
            f"/api/v1/system/users/{user['id']}/roles",
            json={"role_codes": ["teacher", "device_owner"]},
            headers=auth_headers("admin"),
        )
    )
    assert {role["code"] for role in updated_roles["roles"]} == {"teacher", "device_owner"}

    restored_roles = data(
        client.put(
            f"/api/v1/system/users/{user['id']}/roles",
            json={"role_codes": ["teacher"]},
            headers=auth_headers("admin"),
        )
    )
    assert [role["code"] for role in restored_roles["roles"]] == ["teacher"]


def test_system_management_protects_current_and_last_admin() -> None:
    admin = find_user("admin")

    self_disable = client.patch(
        f"/api/v1/system/users/{admin['id']}/status",
        json={"status": "disabled"},
        headers=auth_headers("admin"),
    )
    assert self_disable.status_code == 400

    remove_last_admin = client.put(
        f"/api/v1/system/users/{admin['id']}/roles",
        json={"role_codes": ["lab_admin"]},
        headers=auth_headers("admin"),
    )
    assert remove_last_admin.status_code == 400
