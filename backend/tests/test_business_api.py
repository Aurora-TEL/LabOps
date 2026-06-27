from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

DEVICE_ID = "10000000-0000-0000-0000-000000000001"
RESERVATION_ID = "20000000-0000-0000-0000-000000000002"
REPAIR_REPORT_ID = "30000000-0000-0000-0000-000000000002"
WORK_ORDER_ID = "40000000-0000-0000-0000-000000000002"


def data(response):
    assert response.json()["code"] == 0
    return response.json()["data"]


def auth_headers(username: str = "admin") -> dict[str, str]:
    response = client.post("/api/v1/auth/login", json={"username": username, "password": "labops123"})
    token = data(response)["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_device_list_filter_and_status_update() -> None:
    response = client.get("/api/v1/devices", params={"keyword": "centrifuge", "page_size": 5})

    payload = data(response)
    assert response.status_code == 200
    assert payload["total"] >= 1
    assert payload["items"][0]["code"] == "DEV-001"

    response = client.patch(f"/api/v1/devices/{DEVICE_ID}/status", json={"status": "maintenance", "reason": "planned"})

    payload = data(response)
    assert payload["status"] == "maintenance"


def test_create_device_rejects_duplicate_code() -> None:
    response = client.post(
        "/api/v1/devices",
        json={
            "code": "DEV-001",
            "name": "Duplicate device",
            "status": "available",
            "health_score": 90,
        },
    )

    assert response.status_code == 409
    assert response.json() == {"code": 40900, "message": "device code already exists", "data": None}


def test_reservation_create_and_conflict() -> None:
    start = datetime.now(timezone.utc) + timedelta(days=7)
    end = start + timedelta(hours=2)
    payload = {
        "device_id": DEVICE_ID,
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


def test_repair_report_and_work_order_flow() -> None:
    repair_response = client.post(
        "/api/v1/repair-reports",
        json={"device_id": DEVICE_ID, "fault_type": "software", "description": "Control panel freezes intermittently."},
        headers=auth_headers("student01"),
    )
    repair = data(repair_response)
    assert repair_response.status_code == 201
    assert repair["status"] == "submitted"

    order_response = client.post(
        "/api/v1/work-orders",
        json={"repair_report_id": repair["id"], "assignee_id": None, "priority": "urgent"},
    )
    order = data(order_response)
    assert order_response.status_code == 201
    assert order["status"] == "pending"

    finish_response = client.post(f"/api/v1/work-orders/{order['id']}/finish", json={"result": "Restarted controller."})
    finished = data(finish_response)
    assert finished["status"] == "finished"
    assert finished["finished_at"] is not None

    repair_after_finish = data(client.get(f"/api/v1/repair-reports/{repair['id']}"))
    assert repair_after_finish["status"] == "closed"


def test_dashboard_and_error_shape() -> None:
    summary = data(client.get("/api/v1/dashboard/summary"))
    assert summary["device_total"] >= 3
    assert "open_work_orders" in summary

    trend = data(client.get("/api/v1/dashboard/device-utilization", params={"start_date": "2026-06-01", "end_date": "2026-06-03"}))
    assert len(trend) == 3

    response = client.get("/api/v1/devices/not-a-uuid")
    assert response.status_code == 422
    assert response.json()["code"] == 40000
