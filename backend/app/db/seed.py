from __future__ import annotations

import uuid
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from typing import Any

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models import (
    Device,
    DeviceCategory,
    Lab,
    MaintenanceRecord,
    OperationMetric,
    Permission,
    RepairReport,
    Reservation,
    Role,
    RolePermission,
    User,
    UserRole,
    WorkOrder,
)

NAMESPACE = uuid.UUID("11111111-2222-3333-4444-555555555555")
DEMO_PASSWORD_HASH = "$2b$12$J1H5N0x9o0KT0WqzAgNl2.cStDemoOnlyHashForLabOpsSeedData"


def stable_uuid(name: str) -> uuid.UUID:
    return uuid.uuid5(NAMESPACE, name)


def upsert_by_id(db: Session, model: type[Any], rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    column_names = [column.name for column in model.__table__.columns if column.name not in {"created_at", "updated_at"}]
    rows = [{column_name: row.get(column_name) for column_name in column_names if column_name in row or column_name != "id"} for row in rows]
    statement = insert(model).values(rows)
    update_columns = {
        column.name: getattr(statement.excluded, column.name)
        for column in model.__table__.columns
        if column.name not in {"id", "created_at"}
    }
    db.execute(statement.on_conflict_do_update(index_elements=["id"], set_=update_columns))


def insert_ignore(db: Session, model: type[Any], rows: list[dict[str, Any]], index_elements: list[str]) -> None:
    if rows:
        column_names = [column.name for column in model.__table__.columns if column.name != "created_at"]
        rows = [{column_name: row.get(column_name) for column_name in column_names if column_name in row} for row in rows]
        db.execute(insert(model).values(rows).on_conflict_do_nothing(index_elements=index_elements))


def seed_security(db: Session) -> dict[str, uuid.UUID]:
    role_rows = [
        {"id": stable_uuid("role:student"), "code": "student", "name": "Student", "is_system": True},
        {"id": stable_uuid("role:teacher"), "code": "teacher", "name": "Teacher", "is_system": True},
        {"id": stable_uuid("role:lab_admin"), "code": "lab_admin", "name": "Lab Admin", "is_system": True},
        {"id": stable_uuid("role:system_admin"), "code": "system_admin", "name": "System Admin", "is_system": True},
    ]
    permission_codes = [
        "dashboard:view",
        "analytics:view",
        "device:view",
        "device:create",
        "device:update",
        "device:delete",
        "reservation:view_self",
        "reservation:view_all",
        "reservation:create",
        "reservation:approve",
        "reservation:cancel_self",
        "reservation:cancel_all",
        "repair:view_self",
        "repair:view_all",
        "repair:create",
        "repair:accept",
        "work_order:create",
        "work_order:update",
        "work_order:close",
        "user:manage",
        "role:manage",
        "dictionary:manage",
    ]
    permission_rows = [
        {
            "id": stable_uuid(f"permission:{code}"),
            "code": code,
            "name": code.replace(":", " ").title(),
            "resource": code.split(":")[0],
            "action": code.split(":")[1],
        }
        for code in permission_codes
    ]
    user_rows = [
        {
            "id": stable_uuid("user:student01"),
            "username": "student01",
            "password_hash": DEMO_PASSWORD_HASH,
            "real_name": "Student Demo",
            "email": "student01@example.edu",
            "department": "Mechanical Engineering",
            "student_no": "S2026001",
            "status": "active",
        },
        {
            "id": stable_uuid("user:teacher01"),
            "username": "teacher01",
            "password_hash": DEMO_PASSWORD_HASH,
            "real_name": "Teacher Demo",
            "email": "teacher01@example.edu",
            "department": "Electronic Information",
            "employee_no": "T2026001",
            "status": "active",
        },
        {
            "id": stable_uuid("user:labadmin01"),
            "username": "labadmin01",
            "password_hash": DEMO_PASSWORD_HASH,
            "real_name": "Lab Admin Demo",
            "email": "labadmin01@example.edu",
            "department": "Lab Center",
            "employee_no": "L2026001",
            "status": "active",
        },
        {
            "id": stable_uuid("user:admin"),
            "username": "admin",
            "password_hash": DEMO_PASSWORD_HASH,
            "real_name": "System Admin",
            "email": "admin@example.edu",
            "department": "IT",
            "employee_no": "A2026001",
            "status": "active",
        },
    ]
    upsert_by_id(db, Role, role_rows)
    upsert_by_id(db, Permission, permission_rows)
    upsert_by_id(db, User, user_rows)

    role_ids = {row["code"]: row["id"] for row in role_rows}
    permission_ids = {row["code"]: row["id"] for row in permission_rows}
    user_ids = {row["username"]: row["id"] for row in user_rows}

    insert_ignore(
        db,
        UserRole,
        [
            {"user_id": user_ids["student01"], "role_id": role_ids["student"]},
            {"user_id": user_ids["teacher01"], "role_id": role_ids["teacher"]},
            {"user_id": user_ids["labadmin01"], "role_id": role_ids["lab_admin"]},
            {"user_id": user_ids["admin"], "role_id": role_ids["system_admin"]},
        ],
        ["user_id", "role_id"],
    )
    role_permission_map = {
        "student": ["dashboard:view", "device:view", "reservation:view_self", "reservation:create", "reservation:cancel_self", "repair:view_self", "repair:create"],
        "teacher": ["dashboard:view", "analytics:view", "device:view", "reservation:view_all", "reservation:approve", "repair:view_all"],
        "lab_admin": [code for code in permission_codes if not code.startswith(("user:", "role:"))],
        "system_admin": permission_codes,
    }
    insert_ignore(
        db,
        RolePermission,
        [
            {"role_id": role_ids[role], "permission_id": permission_ids[permission]}
            for role, permissions in role_permission_map.items()
            for permission in permissions
        ],
        ["role_id", "permission_id"],
    )
    return user_ids


def seed_assets(db: Session, user_ids: dict[str, uuid.UUID]) -> tuple[dict[str, uuid.UUID], dict[str, uuid.UUID]]:
    labs = [
        {"id": stable_uuid("lab:smart-manufacturing"), "code": "LAB-SM", "name": "Smart Manufacturing Lab", "location": "Building A 301", "manager_id": user_ids["labadmin01"], "is_active": True},
        {"id": stable_uuid("lab:electronics"), "code": "LAB-EI", "name": "Electronic Information Lab", "location": "Building B 208", "manager_id": user_ids["teacher01"], "is_active": True},
        {"id": stable_uuid("lab:iot"), "code": "LAB-IOT", "name": "Sensor and IoT Lab", "location": "Building C 512", "manager_id": user_ids["labadmin01"], "is_active": True},
    ]
    categories = [
        {"id": stable_uuid("category:analysis"), "code": "analysis", "name": "Analysis and Testing", "sort_order": 10, "is_active": True},
        {"id": stable_uuid("category:manufacturing"), "code": "manufacturing", "name": "Manufacturing", "sort_order": 20, "is_active": True},
        {"id": stable_uuid("category:electronics"), "code": "electronics", "name": "Electronic Information", "sort_order": 30, "is_active": True},
        {"id": stable_uuid("category:biology"), "code": "biology", "name": "Biology", "sort_order": 40, "is_active": True},
        {"id": stable_uuid("category:general"), "code": "general", "name": "General Instruments", "sort_order": 50, "is_active": True},
    ]
    upsert_by_id(db, Lab, labs)
    upsert_by_id(db, DeviceCategory, categories)
    lab_ids = {row["code"]: row["id"] for row in labs}
    category_ids = {row["code"]: row["id"] for row in categories}

    devices = [
        ("DEV-3DP-A01", "3D Printer A01", "manufacturing", "LAB-SM", "idle", "98.00"),
        ("DEV-LAS-L01", "Laser Cutter L01", "manufacturing", "LAB-SM", "in_use", "91.50"),
        ("DEV-CNC-C01", "Desktop CNC C01", "manufacturing", "LAB-SM", "idle", "95.00"),
        ("DEV-OSC-01", "Oscilloscope OSC-01", "electronics", "LAB-EI", "idle", "97.50"),
        ("DEV-NET-01", "Network Analyzer NET-01", "electronics", "LAB-EI", "maintenance", "76.00"),
        ("DEV-SEN-S01", "Sensor Bench S01", "electronics", "LAB-IOT", "fault", "62.00"),
        ("DEV-IOT-GW01", "IoT Gateway GW01", "general", "LAB-IOT", "idle", "93.00"),
        ("DEV-MIC-M01", "Microscope M01", "analysis", "LAB-EI", "idle", "96.00"),
        ("DEV-BIO-B01", "Bioreactor B01", "biology", "LAB-IOT", "disabled", "88.00"),
    ]
    device_rows = [
        {
            "id": stable_uuid(f"device:{code}"),
            "code": code,
            "name": name,
            "category_id": category_ids[category],
            "lab_id": lab_ids[lab],
            "manager_id": user_ids["labadmin01"],
            "status": status,
            "health_score": Decimal(score),
            "model": f"{code}-MODEL",
            "manufacturer": "LabOps Demo",
            "serial_number": f"SN-{code}",
            "purchase_date": date(2025, 9, 1),
            "purchase_price": Decimal("12000.00"),
            "location_detail": "Main workbench",
        }
        for code, name, category, lab, status, score in devices
    ]
    upsert_by_id(db, Device, device_rows)
    return lab_ids, {row["code"]: row["id"] for row in device_rows}


def seed_business(db: Session, user_ids: dict[str, uuid.UUID], lab_ids: dict[str, uuid.UUID], device_ids: dict[str, uuid.UUID]) -> None:
    now = datetime.now(UTC).replace(minute=0, second=0, microsecond=0)
    reservations = [
        ("RSV-20260626-001", "DEV-3DP-A01", "approved", now + timedelta(days=1, hours=1), now + timedelta(days=1, hours=3), user_ids["teacher01"]),
        ("RSV-20260626-002", "DEV-OSC-01", "pending", now + timedelta(days=1, hours=4), now + timedelta(days=1, hours=6), None),
        ("RSV-20260626-003", "DEV-MIC-M01", "completed", now - timedelta(days=2, hours=2), now - timedelta(days=2), user_ids["teacher01"]),
        ("RSV-20260626-004", "DEV-CNC-C01", "rejected", now + timedelta(days=2), now + timedelta(days=2, hours=2), user_ids["teacher01"]),
        ("RSV-20260626-005", "DEV-IOT-GW01", "cancelled", now - timedelta(days=1), now - timedelta(days=1) + timedelta(hours=2), None),
    ]
    upsert_by_id(
        db,
        Reservation,
        [
            {
                "id": stable_uuid(f"reservation:{no}"),
                "reservation_no": no,
                "device_id": device_ids[device_code],
                "applicant_id": user_ids["student01"],
                "approver_id": approver_id,
                "start_time": start_time,
                "end_time": end_time,
                "purpose": "Demo experiment booking",
                "participant_count": 2,
                "status": status,
                "reject_reason": "Schedule conflict" if status == "rejected" else None,
                "cancel_reason": "User cancelled" if status == "cancelled" else None,
                "approved_at": now if status in {"approved", "completed"} else None,
                "cancelled_at": now if status == "cancelled" else None,
                "completed_at": now if status == "completed" else None,
            }
            for no, device_code, status, start_time, end_time, approver_id in reservations
        ],
    )

    reports = [
        ("REP-20260626-001", "DEV-SEN-S01", "sensor", "urgent", "assigned"),
        ("REP-20260626-002", "DEV-NET-01", "network", "high", "processing"),
        ("REP-20260626-003", "DEV-LAS-L01", "mechanical", "medium", "closed"),
        ("REP-20260626-004", "DEV-MIC-M01", "optical", "low", "submitted"),
    ]
    upsert_by_id(
        db,
        RepairReport,
        [
            {
                "id": stable_uuid(f"repair:{no}"),
                "report_no": no,
                "device_id": device_ids[device_code],
                "reporter_id": user_ids["student01"],
                "accepted_by_id": user_ids["labadmin01"] if status != "submitted" else None,
                "fault_type": fault_type,
                "urgency": urgency,
                "description": f"{device_code} demo fault report",
                "status": status,
                "accepted_at": now - timedelta(days=1) if status != "submitted" else None,
                "closed_at": now if status == "closed" else None,
                "close_note": "Resolved during demo maintenance" if status == "closed" else None,
            }
            for no, device_code, fault_type, urgency, status in reports
        ],
    )

    work_orders = [
        ("WO-20260626-001", "REP-20260626-001", "DEV-SEN-S01", "urgent", "assigned"),
        ("WO-20260626-002", "REP-20260626-002", "DEV-NET-01", "high", "processing"),
        ("WO-20260626-003", "REP-20260626-003", "DEV-LAS-L01", "medium", "closed"),
    ]
    upsert_by_id(
        db,
        WorkOrder,
        [
            {
                "id": stable_uuid(f"work-order:{no}"),
                "work_order_no": no,
                "repair_report_id": stable_uuid(f"repair:{report_no}"),
                "device_id": device_ids[device_code],
                "creator_id": user_ids["labadmin01"],
                "assignee_id": user_ids["labadmin01"],
                "priority": priority,
                "status": status,
                "planned_start_at": now - timedelta(hours=4),
                "planned_end_at": now + timedelta(hours=4),
                "started_at": now - timedelta(hours=2) if status in {"processing", "closed"} else None,
                "finished_at": now - timedelta(hours=1) if status == "closed" else None,
                "closed_at": now if status == "closed" else None,
                "process_note": "Demo maintenance workflow",
                "result": "Device restored" if status == "closed" else None,
                "cost_amount": Decimal("350.00") if status == "closed" else None,
            }
            for no, report_no, device_code, priority, status in work_orders
        ],
    )

    maintenance_rows = [
        ("DEV-LAS-L01", "WO-20260626-003", "repair", "Laser cutter repair", "Device restored", Decimal("350.00")),
        ("DEV-3DP-A01", None, "routine", "Monthly cleaning", "Cleaned and calibrated", Decimal("80.00")),
        ("DEV-OSC-01", None, "calibration", "Signal calibration", "Calibration passed", Decimal("120.00")),
        ("DEV-IOT-GW01", None, "replacement", "Antenna replacement", "Signal improved", Decimal("60.00")),
    ]
    upsert_by_id(
        db,
        MaintenanceRecord,
        [
            {
                "id": stable_uuid(f"maintenance:{device_code}:{maintenance_type}"),
                "device_id": device_ids[device_code],
                "work_order_id": stable_uuid(f"work-order:{work_order_no}") if work_order_no else None,
                "maintainer_id": user_ids["labadmin01"],
                "maintenance_type": maintenance_type,
                "title": title,
                "content": f"{title} for demo dataset",
                "result": result,
                "cost_amount": cost,
                "maintained_at": now - timedelta(days=index + 1),
                "next_maintenance_at": now + timedelta(days=30),
            }
            for index, (device_code, work_order_no, maintenance_type, title, result, cost) in enumerate(maintenance_rows)
        ],
    )

    metric_rows = []
    for index in range(30):
        metric_date = date.today() - timedelta(days=29 - index)
        metric_rows.append(
            {
                "id": stable_uuid(f"metric:daily:{metric_date.isoformat()}"),
                "metric_date": metric_date,
                "period_type": "daily",
                "lab_id": None,
                "device_id": None,
                "total_devices": len(device_ids),
                "online_devices": 7,
                "idle_devices": 5,
                "fault_devices": 1,
                "reservation_count": 5 + (index % 6),
                "approved_reservation_count": 3 + (index % 4),
                "completed_reservation_count": 2 + (index % 3),
                "repair_report_count": index % 4,
                "closed_repair_count": index % 2,
                "utilization_rate": Decimal(str(52 + (index % 12) * 2)),
                "avg_repair_hours": Decimal("5.50"),
            }
        )
    for index in range(8):
        metric_date = date.today() - timedelta(weeks=7 - index)
        metric_rows.append(
            {
                "id": stable_uuid(f"metric:weekly:{metric_date.isoformat()}"),
                "metric_date": metric_date,
                "period_type": "weekly",
                "lab_id": lab_ids["LAB-SM"],
                "device_id": None,
                "total_devices": 3,
                "online_devices": 3,
                "idle_devices": 2,
                "fault_devices": 0,
                "reservation_count": 18 + index,
                "approved_reservation_count": 14 + index,
                "completed_reservation_count": 12 + index,
                "repair_report_count": index % 3,
                "closed_repair_count": index % 2,
                "utilization_rate": Decimal(str(60 + index * 2)),
                "avg_repair_hours": Decimal("4.00"),
            }
        )
    upsert_by_id(db, OperationMetric, metric_rows)


def seed(db: Session) -> None:
    user_ids = seed_security(db)
    lab_ids, device_ids = seed_assets(db, user_ids)
    seed_business(db, user_ids, lab_ids, device_ids)


def main() -> None:
    with SessionLocal() as db:
        seed(db)
        db.commit()
    print("LabOps demo seed data loaded.")


if __name__ == "__main__":
    main()
