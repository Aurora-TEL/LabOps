from app.models import Base


def test_core_database_tables_are_registered() -> None:
    expected_tables = {
        "users",
        "roles",
        "permissions",
        "user_roles",
        "role_permissions",
        "labs",
        "device_categories",
        "devices",
        "reservations",
        "repair_reports",
        "work_orders",
        "maintenance_records",
        "operation_metrics",
    }

    assert expected_tables.issubset(Base.metadata.tables.keys())


def test_reservation_conflict_contract_is_named_in_metadata() -> None:
    reservation_constraints = {constraint.name for constraint in Base.metadata.tables["reservations"].constraints}

    assert "ck_reservations_status" in reservation_constraints
    assert "ck_reservations_time_range" in reservation_constraints
