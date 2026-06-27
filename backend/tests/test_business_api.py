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
    payload = data(client.get("/api/v1/devices", params={"keyword": "3D Printer", "page_size": 1}))
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
    )
    assert response.status_code == 201
    return data(response)


def test_device_list_filter_create_and_status_update() -> None:
    device = seeded_device()
    assert device["code"] == "DEV-3DP-A01"

    response = client.patch(f"/api/v1/devices/{device['id']}/status", json={"status": "maintenance", "reason": "planned"})
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

    repair_after_assignment = data(client.get(f"/api/v1/repair-reports/{repair['id']}"))
    assert repair_after_assignment["status"] == "assigned"

    finish_response = client.post(f"/api/v1/work-orders/{order['id']}/finish", json={"result": "Restarted controller."})
    finished = data(finish_response)
    assert finished["status"] == "finished"
    assert finished["finished_at"] is not None

    repair_after_finish = data(client.get(f"/api/v1/repair-reports/{repair['id']}"))
    assert repair_after_finish["status"] == "closed"


def test_dashboard_aggregates_database_rows_and_preserves_error_shape() -> None:
    summary = data(client.get("/api/v1/dashboard/summary"))
    assert summary["device_total"] >= 9
    assert "open_work_orders" in summary

    trend = data(client.get("/api/v1/dashboard/device-utilization", params={"start_date": "2026-06-01", "end_date": "2026-06-03"}))
    assert len(trend) == 3

    statuses = data(client.get("/api/v1/dashboard/reservation-status"))
    assert {item["status"] for item in statuses} >= {"pending", "approved", "rejected", "canceled", "completed"}

    response = client.get("/api/v1/devices/not-a-uuid")
    assert response.status_code == 422
    assert response.json()["code"] == 40000
