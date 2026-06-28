from datetime import datetime, timedelta, timezone
from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def data(response):
    assert response.json()["code"] == 0
    return response.json()["data"]


def auth_headers(username: str = "admin") -> dict[str, str]:
    response = client.post("/api/v1/auth/login", json={"username": username, "password": "labops123"})
    token = data(response)["access_token"]
    return {"Authorization": f"Bearer {token}"}


def seeded_device() -> dict:
    payload = data(client.get("/api/v1/devices", params={"keyword": "3D Printer", "page_size": 1}, headers=auth_headers("admin")))
    assert payload["total"] >= 1
    return payload["items"][0]


def device_by_keyword(keyword: str, username: str = "admin") -> dict:
    payload = data(client.get("/api/v1/devices", params={"keyword": keyword, "page_size": 1}, headers=auth_headers(username)))
    assert payload["total"] >= 1
    return payload["items"][0]


def create_test_device() -> dict:
    response = client.post(
        "/api/v1/devices",
        json={
            "code": f"TEST-DEV-{uuid4().hex[:8]}",
            "name": "API created device",
            "status": "available",
            "health_score": 90,
        },
        headers=auth_headers("admin"),
    )
    assert response.status_code == 201
    return data(response)


def test_device_list_filter_create_and_status_update() -> None:
    device = seeded_device()
    assert device["code"] == "DEV-3DP-A01"

    response = client.patch(f"/api/v1/devices/{device['id']}/status", json={"status": "maintenance", "reason": "planned"}, headers=auth_headers("admin"))
    assert data(response)["status"] == "maintenance"

    created = create_test_device()
    assert created["status"] == "available"
    assert created["lab_id"] is not None
    assert created["category_id"] is not None


def test_create_device_rejects_duplicate_code() -> None:
    response = client.post(
        "/api/v1/devices",
        json={
            "code": "DEV-3DP-A01",
            "name": "Duplicate device",
            "status": "available",
            "health_score": 90,
        },
        headers=auth_headers("admin"),
    )

    assert response.status_code == 409
    assert response.json() == {"code": 40900, "message": "device code already exists", "data": None}


def test_reservation_create_approve_and_conflict_against_database() -> None:
    device = create_test_device()
    start = datetime.now(timezone.utc) + timedelta(days=14, minutes=uuid4().int % 1000)
    end = start + timedelta(hours=2)
    payload = {
        "device_id": device["id"],
        "start_time": start.isoformat(),
        "end_time": end.isoformat(),
        "purpose": "Compatibility testing",
    }

    create_response = client.post("/api/v1/reservations", json=payload, headers=auth_headers("student01"))
    created = data(create_response)
    assert create_response.status_code == 201
    assert created["status"] == "pending"

    approve_response = client.post(f"/api/v1/reservations/{created['id']}/approve", headers=auth_headers("admin"))
    assert data(approve_response)["status"] == "approved"

    conflict_response = client.post("/api/v1/reservations", json=payload, headers=auth_headers("student01"))
    assert conflict_response.status_code == 409
    assert conflict_response.json()["code"] == 40900


def test_reservation_calendar_and_availability_scope() -> None:
    device = create_test_device()
    start = datetime.now(timezone.utc) + timedelta(days=35, minutes=uuid4().int % 1000)
    end = start + timedelta(hours=2)
    payload = {
        "device_id": device["id"],
        "start_time": start.isoformat(),
        "end_time": end.isoformat(),
        "purpose": "Calendar availability flow",
    }

    reservation = data(client.post("/api/v1/reservations", json=payload, headers=auth_headers("ordinary01")))
    approved = data(client.post(f"/api/v1/reservations/{reservation['id']}/approve", headers=auth_headers("admin")))
    assert approved["status"] == "approved"

    calendar = data(
        client.get(
            "/api/v1/reservations/calendar",
            params={
                "start_time": (start - timedelta(hours=1)).isoformat(),
                "end_time": (end + timedelta(hours=1)).isoformat(),
                "device_id": device["id"],
            },
            headers=auth_headers("admin"),
        )
    )
    assert any(item["id"] == reservation["id"] and item["reservation_no"].startswith("RSV-") for item in calendar)

    ordinary_calendar = data(
        client.get(
            "/api/v1/reservations/calendar",
            params={"start_time": (start - timedelta(hours=1)).isoformat(), "end_time": (end + timedelta(hours=1)).isoformat()},
            headers=auth_headers("ordinary01"),
        )
    )
    assert all(item["applicant_id"] == reservation["applicant_id"] for item in ordinary_calendar)

    occupied = data(
        client.get(
            "/api/v1/reservations/availability",
            params={"device_id": device["id"], "start_time": start.isoformat(), "end_time": end.isoformat()},
            headers=auth_headers("ordinary01"),
        )
    )
    assert occupied["available"] is False
    assert occupied["conflict_count"] >= 1

    adjacent = data(
        client.get(
            "/api/v1/reservations/availability",
            params={"device_id": device["id"], "start_time": end.isoformat(), "end_time": (end + timedelta(hours=1)).isoformat()},
            headers=auth_headers("ordinary01"),
        )
    )
    assert adjacent["available"] is True
    assert adjacent["conflict_count"] == 0


def test_repair_report_and_work_order_state_flow_updates_related_report() -> None:
    device = seeded_device()
    repair_response = client.post(
        "/api/v1/repair-reports",
        json={"device_id": device["id"], "fault_type": "software", "description": "Control panel freezes intermittently."},
        headers=auth_headers("student01"),
    )
    repair = data(repair_response)
    assert repair_response.status_code == 201
    assert repair["status"] == "submitted"

    order_response = client.post(
        "/api/v1/work-orders",
        json={"repair_report_id": repair["id"], "assignee_id": None, "priority": "urgent"},
        headers=auth_headers("admin"),
    )
    order = data(order_response)
    assert order_response.status_code == 201
    assert order["status"] == "pending"

    repair_after_assignment = data(client.get(f"/api/v1/repair-reports/{repair['id']}", headers=auth_headers("admin")))
    assert repair_after_assignment["status"] == "assigned"

    finish_response = client.post(f"/api/v1/work-orders/{order['id']}/finish", json={"result": "Restarted controller."}, headers=auth_headers("admin"))
    finished = data(finish_response)
    assert finished["status"] == "finished"
    assert finished["finished_at"] is not None

    repair_after_finish = data(client.get(f"/api/v1/repair-reports/{repair['id']}", headers=auth_headers("admin")))
    assert repair_after_finish["status"] == "closed"


def test_dashboard_aggregates_database_rows_and_preserves_error_shape() -> None:
    summary = data(client.get("/api/v1/dashboard/summary", headers=auth_headers("admin")))
    assert summary["device_total"] >= 9
    assert "open_work_orders" in summary

    trend = data(client.get("/api/v1/dashboard/device-utilization", params={"start_date": "2026-06-01", "end_date": "2026-06-03"}, headers=auth_headers("admin")))
    assert len(trend) == 3

    statuses = data(client.get("/api/v1/dashboard/reservation-status", headers=auth_headers("admin")))
    assert {item["status"] for item in statuses} >= {"pending", "approved", "rejected", "canceled", "completed"}

    response = client.get("/api/v1/devices/not-a-uuid", headers=auth_headers("admin"))
    assert response.status_code == 422
    assert response.json()["code"] == 40000


def test_ordinary_user_is_limited_to_self_service_actions() -> None:
    device = create_test_device()
    start = datetime.now(timezone.utc) + timedelta(days=21, minutes=uuid4().int % 1000)
    payload = {
        "device_id": device["id"],
        "start_time": start.isoformat(),
        "end_time": (start + timedelta(hours=1)).isoformat(),
        "purpose": "Ordinary user booking",
    }

    create_response = client.post("/api/v1/reservations", json=payload, headers=auth_headers("ordinary01"))
    reservation = data(create_response)
    assert create_response.status_code == 201

    own_list = data(client.get("/api/v1/reservations", headers=auth_headers("ordinary01")))
    assert all(item["applicant_id"] == reservation["applicant_id"] for item in own_list["items"])

    assert client.post(f"/api/v1/reservations/{reservation['id']}/approve", headers=auth_headers("ordinary01")).status_code == 403
    assert client.post("/api/v1/devices", json={"code": f"NOPE-{uuid4().hex[:6]}", "name": "Nope"}, headers=auth_headers("ordinary01")).status_code == 403

    repair_response = client.post(
        "/api/v1/repair-reports",
        json={"device_id": device["id"], "fault_type": "hardware", "description": "Need ordinary-user repair test."},
        headers=auth_headers("ordinary01"),
    )
    assert data(repair_response)["status"] == "submitted"
    assert client.post("/api/v1/work-orders", json={"repair_report_id": data(repair_response)["id"], "priority": "low"}, headers=auth_headers("ordinary01")).status_code == 403


def test_device_owner_scope_and_manager_protection() -> None:
    owner_devices = data(client.get("/api/v1/devices", params={"page_size": 20}, headers=auth_headers("owner01")))
    assert owner_devices["total"] >= 1
    owned_device = owner_devices["items"][0]
    assert owned_device["manager_id"] is not None

    status_response = client.patch(
        f"/api/v1/devices/{owned_device['id']}/status",
        json={"status": "maintenance", "reason": "owner planned maintenance"},
        headers=auth_headers("owner01"),
    )
    assert data(status_response)["status"] == "maintenance"

    transfer_response = client.put(
        f"/api/v1/devices/{owned_device['id']}",
        json={"manager_id": "00000000-0000-0000-0000-000000000104"},
        headers=auth_headers("owner01"),
    )
    assert transfer_response.status_code == 403

    non_owner_device = device_by_keyword("Network Analyzer", "admin")
    assert client.get(f"/api/v1/devices/{non_owner_device['id']}", headers=auth_headers("owner01")).status_code == 403


def test_device_owner_cannot_manage_non_owned_workflow() -> None:
    non_owner_device = device_by_keyword("Network Analyzer", "admin")
    repair_response = client.post(
        "/api/v1/repair-reports",
        json={"device_id": non_owner_device["id"], "fault_type": "network", "description": "Non-owned device repair."},
        headers=auth_headers("ordinary01"),
    )
    repair = data(repair_response)

    order_response = client.post(
        "/api/v1/work-orders",
        json={"repair_report_id": repair["id"], "priority": "high"},
        headers=auth_headers("owner01"),
    )
    assert order_response.status_code == 403


def test_notifications_and_audit_log_flow() -> None:
    device = device_by_keyword("3D Printer", "admin")
    start = datetime.now(timezone.utc) + timedelta(days=28, minutes=uuid4().int % 1000)
    payload = {
        "device_id": device["id"],
        "start_time": start.isoformat(),
        "end_time": (start + timedelta(hours=1)).isoformat(),
        "purpose": "Notification flow test",
    }

    created = data(client.post("/api/v1/reservations", json=payload, headers=auth_headers("ordinary01")))

    owner_notifications = data(client.get("/api/v1/notifications", headers=auth_headers("owner01")))
    assert owner_notifications["total"] >= 1
    assert any(item["business_id"] == created["id"] for item in owner_notifications["items"])

    approved = data(client.post(f"/api/v1/reservations/{created['id']}/approve", headers=auth_headers("owner01")))
    assert approved["status"] == "approved"

    ordinary_notifications = data(client.get("/api/v1/notifications", headers=auth_headers("ordinary01")))
    unread = [item for item in ordinary_notifications["items"] if not item["is_read"]]
    assert unread

    marked = data(client.patch(f"/api/v1/notifications/{unread[0]['id']}/read", headers=auth_headers("ordinary01")))
    assert marked["is_read"] is True

    audit_logs = data(client.get("/api/v1/audit-logs", params={"resource_type": "reservation"}, headers=auth_headers("admin")))
    assert audit_logs["total"] >= 1
    assert any(item["resource_id"] == created["id"] for item in audit_logs["items"])
    assert client.get("/api/v1/audit-logs", headers=auth_headers("ordinary01")).status_code == 403


def test_maintenance_records_scope_and_create() -> None:
    owned_device = device_by_keyword("3D Printer", "owner01")
    non_owner_device = device_by_keyword("Network Analyzer", "admin")

    existing = data(
        client.get(
            "/api/v1/maintenance-records",
            params={"device_id": owned_device["id"]},
            headers=auth_headers("owner01"),
        )
    )
    assert existing["total"] >= 1

    forbidden = client.get(
        "/api/v1/maintenance-records",
        params={"device_id": non_owner_device["id"]},
        headers=auth_headers("owner01"),
    )
    assert forbidden.status_code == 403

    created = data(
        client.post(
            "/api/v1/maintenance-records",
            json={
                "device_id": owned_device["id"],
                "maintenance_type": "routine",
                "title": "Owner routine inspection",
                "content": "Checked nozzle, rail and safety cover during API test.",
                "result": "Passed",
            },
            headers=auth_headers("owner01"),
        )
    )
    assert created["device_id"] == owned_device["id"]
    assert created["maintenance_type"] == "routine"

    assert (
        client.post(
            "/api/v1/maintenance-records",
            json={
                "device_id": non_owner_device["id"],
                "maintenance_type": "routine",
                "title": "Should be forbidden",
                "content": "Owner cannot maintain non-owned devices.",
            },
            headers=auth_headers("owner01"),
        ).status_code
        == 403
    )
