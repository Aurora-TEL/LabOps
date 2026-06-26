"""initial LabOps database

Revision ID: 202606260001
Revises:
Create Date: 2026-06-26
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "202606260001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def uuid_pk() -> sa.Column:
    return sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()"))


def timestamps() -> tuple[sa.Column, sa.Column]:
    return (
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")
    op.execute("CREATE EXTENSION IF NOT EXISTS btree_gist")

    op.create_table(
        "users",
        uuid_pk(),
        sa.Column("username", sa.String(64), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("real_name", sa.String(64), nullable=False),
        sa.Column("email", sa.String(128), nullable=True),
        sa.Column("phone", sa.String(32), nullable=True),
        sa.Column("department", sa.String(128), nullable=True),
        sa.Column("student_no", sa.String(64), nullable=True),
        sa.Column("employee_no", sa.String(64), nullable=True),
        sa.Column("status", sa.String(32), nullable=False, server_default=sa.text("'active'")),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        *timestamps(),
        sa.CheckConstraint("status IN ('active','disabled','locked')", name="ck_users_status"),
        sa.UniqueConstraint("username"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("student_no"),
        sa.UniqueConstraint("employee_no"),
    )
    op.create_index("idx_users_status", "users", ["status"])
    op.create_index("idx_users_real_name", "users", ["real_name"])
    op.create_index("uk_users_lower_username", "users", [sa.text("lower(username)")], unique=True)
    op.create_index("uk_users_lower_email", "users", [sa.text("lower(email)")], unique=True, postgresql_where=sa.text("email IS NOT NULL"))

    op.create_table(
        "roles",
        uuid_pk(),
        sa.Column("code", sa.String(64), nullable=False),
        sa.Column("name", sa.String(64), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_system", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        *timestamps(),
        sa.UniqueConstraint("code"),
    )

    op.create_table(
        "permissions",
        uuid_pk(),
        sa.Column("code", sa.String(128), nullable=False),
        sa.Column("name", sa.String(64), nullable=False),
        sa.Column("resource", sa.String(64), nullable=False),
        sa.Column("action", sa.String(64), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        *timestamps(),
        sa.UniqueConstraint("code"),
    )
    op.create_index("idx_permissions_resource_action", "permissions", ["resource", "action"])

    op.create_table(
        "user_roles",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("role_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("idx_user_roles_role_id", "user_roles", ["role_id"])

    op.create_table(
        "role_permissions",
        sa.Column("role_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("permission_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("idx_role_permissions_permission_id", "role_permissions", ["permission_id"])

    op.create_table(
        "labs",
        uuid_pk(),
        sa.Column("code", sa.String(64), nullable=False),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("location", sa.String(255), nullable=False),
        sa.Column("manager_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("contact_phone", sa.String(32), nullable=True),
        sa.Column("opening_hours", sa.String(128), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        *timestamps(),
        sa.UniqueConstraint("code"),
    )
    op.create_index("idx_labs_manager_id", "labs", ["manager_id"])
    op.create_index("idx_labs_is_active", "labs", ["is_active"])

    op.create_table(
        "device_categories",
        uuid_pk(),
        sa.Column("parent_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("device_categories.id", ondelete="SET NULL"), nullable=True),
        sa.Column("code", sa.String(64), nullable=False),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        *timestamps(),
        sa.UniqueConstraint("code"),
    )
    op.create_index("idx_device_categories_parent_id", "device_categories", ["parent_id"])
    op.create_index("idx_device_categories_is_active", "device_categories", ["is_active"])

    op.create_table(
        "devices",
        uuid_pk(),
        sa.Column("code", sa.String(64), nullable=False),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("category_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("device_categories.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("lab_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("labs.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("manager_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("status", sa.String(32), nullable=False, server_default=sa.text("'idle'")),
        sa.Column("health_score", sa.Numeric(5, 2), nullable=False, server_default=sa.text("100.00")),
        sa.Column("model", sa.String(128), nullable=True),
        sa.Column("manufacturer", sa.String(128), nullable=True),
        sa.Column("serial_number", sa.String(128), nullable=True),
        sa.Column("purchase_date", sa.Date(), nullable=True),
        sa.Column("purchase_price", sa.Numeric(12, 2), nullable=True),
        sa.Column("location_detail", sa.String(255), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        *timestamps(),
        sa.CheckConstraint("status IN ('idle','in_use','maintenance','fault','disabled')", name="ck_devices_status"),
        sa.CheckConstraint("health_score >= 0 AND health_score <= 100", name="ck_devices_health_score"),
        sa.CheckConstraint("purchase_price IS NULL OR purchase_price >= 0", name="ck_devices_purchase_price"),
        sa.UniqueConstraint("code"),
        sa.UniqueConstraint("serial_number"),
    )
    for name, columns in {
        "idx_devices_category_id": ["category_id"],
        "idx_devices_lab_id": ["lab_id"],
        "idx_devices_manager_id": ["manager_id"],
        "idx_devices_status": ["status"],
        "idx_devices_lab_status": ["lab_id", "status"],
        "idx_devices_category_status": ["category_id", "status"],
    }.items():
        op.create_index(name, "devices", columns)

    op.create_table(
        "reservations",
        uuid_pk(),
        sa.Column("reservation_no", sa.String(64), nullable=False),
        sa.Column("device_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("devices.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("applicant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("approver_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("start_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("purpose", sa.Text(), nullable=False),
        sa.Column("participant_count", sa.Integer(), nullable=False, server_default=sa.text("1")),
        sa.Column("status", sa.String(32), nullable=False, server_default=sa.text("'pending'")),
        sa.Column("reject_reason", sa.Text(), nullable=True),
        sa.Column("cancel_reason", sa.Text(), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("remark", sa.Text(), nullable=True),
        *timestamps(),
        sa.CheckConstraint("status IN ('pending','approved','rejected','cancelled','completed')", name="ck_reservations_status"),
        sa.CheckConstraint("start_time < end_time", name="ck_reservations_time_range"),
        sa.CheckConstraint("participant_count > 0", name="ck_reservations_participant_count"),
        sa.UniqueConstraint("reservation_no"),
    )
    for name, columns in {
        "idx_reservations_device_time": ["device_id", "start_time", "end_time"],
        "idx_reservations_applicant_id": ["applicant_id"],
        "idx_reservations_approver_id": ["approver_id"],
        "idx_reservations_status": ["status"],
        "idx_reservations_start_time": ["start_time"],
        "idx_reservations_device_status": ["device_id", "status"],
    }.items():
        op.create_index(name, "reservations", columns)
    op.execute(
        """
        ALTER TABLE reservations
        ADD CONSTRAINT ex_reservations_device_time
        EXCLUDE USING gist (
          device_id WITH =,
          tstzrange(start_time, end_time, '[)') WITH &&
        )
        WHERE (status = 'approved')
        """
    )

    op.create_table(
        "repair_reports",
        uuid_pk(),
        sa.Column("report_no", sa.String(64), nullable=False),
        sa.Column("device_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("devices.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("reporter_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("accepted_by_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("fault_type", sa.String(64), nullable=False),
        sa.Column("urgency", sa.String(32), nullable=False, server_default=sa.text("'medium'")),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("image_url", sa.String(512), nullable=True),
        sa.Column("status", sa.String(32), nullable=False, server_default=sa.text("'submitted'")),
        sa.Column("accepted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("close_note", sa.Text(), nullable=True),
        *timestamps(),
        sa.CheckConstraint("status IN ('submitted','accepted','assigned','processing','finished','closed')", name="ck_repair_reports_status"),
        sa.CheckConstraint("urgency IN ('low','medium','high','urgent')", name="ck_repair_reports_urgency"),
        sa.UniqueConstraint("report_no"),
    )
    for name, columns in {
        "idx_repair_reports_device_id": ["device_id"],
        "idx_repair_reports_reporter_id": ["reporter_id"],
        "idx_repair_reports_status": ["status"],
        "idx_repair_reports_fault_type": ["fault_type"],
        "idx_repair_reports_created_at": ["created_at"],
        "idx_repair_reports_device_status": ["device_id", "status"],
    }.items():
        op.create_index(name, "repair_reports", columns)

    op.create_table(
        "work_orders",
        uuid_pk(),
        sa.Column("work_order_no", sa.String(64), nullable=False),
        sa.Column("repair_report_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("repair_reports.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("device_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("devices.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("creator_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("assignee_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("priority", sa.String(32), nullable=False, server_default=sa.text("'medium'")),
        sa.Column("status", sa.String(32), nullable=False, server_default=sa.text("'assigned'")),
        sa.Column("planned_start_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("planned_end_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("process_note", sa.Text(), nullable=True),
        sa.Column("result", sa.Text(), nullable=True),
        sa.Column("cost_amount", sa.Numeric(12, 2), nullable=True),
        *timestamps(),
        sa.CheckConstraint("priority IN ('low','medium','high','urgent')", name="ck_work_orders_priority"),
        sa.CheckConstraint("status IN ('assigned','processing','finished','closed')", name="ck_work_orders_status"),
        sa.CheckConstraint(
            "planned_start_at IS NULL OR planned_end_at IS NULL OR planned_start_at < planned_end_at",
            name="ck_work_orders_planned_range",
        ),
        sa.CheckConstraint("cost_amount IS NULL OR cost_amount >= 0", name="ck_work_orders_cost_amount"),
        sa.UniqueConstraint("work_order_no"),
    )
    for name, columns in {
        "idx_work_orders_repair_report_id": ["repair_report_id"],
        "idx_work_orders_device_id": ["device_id"],
        "idx_work_orders_assignee_id": ["assignee_id"],
        "idx_work_orders_status": ["status"],
        "idx_work_orders_priority": ["priority"],
        "idx_work_orders_created_at": ["created_at"],
        "idx_work_orders_device_status": ["device_id", "status"],
    }.items():
        op.create_index(name, "work_orders", columns)

    op.create_table(
        "maintenance_records",
        uuid_pk(),
        sa.Column("device_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("devices.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("work_order_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("work_orders.id", ondelete="SET NULL"), nullable=True),
        sa.Column("maintainer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("maintenance_type", sa.String(32), nullable=False),
        sa.Column("title", sa.String(128), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("result", sa.Text(), nullable=True),
        sa.Column("cost_amount", sa.Numeric(12, 2), nullable=True),
        sa.Column("maintained_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("next_maintenance_at", sa.DateTime(timezone=True), nullable=True),
        *timestamps(),
        sa.CheckConstraint(
            "maintenance_type IN ('routine','repair','calibration','replacement','enable','disable')",
            name="ck_maintenance_records_type",
        ),
        sa.CheckConstraint("cost_amount IS NULL OR cost_amount >= 0", name="ck_maintenance_records_cost_amount"),
    )
    for name, columns in {
        "idx_maintenance_records_device_id": ["device_id"],
        "idx_maintenance_records_work_order_id": ["work_order_id"],
        "idx_maintenance_records_maintainer_id": ["maintainer_id"],
        "idx_maintenance_records_type": ["maintenance_type"],
        "idx_maintenance_records_maintained_at": ["maintained_at"],
        "idx_maintenance_records_device_time": ["device_id", "maintained_at"],
    }.items():
        op.create_index(name, "maintenance_records", columns)

    op.create_table(
        "operation_metrics",
        uuid_pk(),
        sa.Column("metric_date", sa.Date(), nullable=False),
        sa.Column("period_type", sa.String(32), nullable=False),
        sa.Column("lab_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("labs.id", ondelete="SET NULL"), nullable=True),
        sa.Column("device_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("devices.id", ondelete="SET NULL"), nullable=True),
        sa.Column("total_devices", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("online_devices", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("idle_devices", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("fault_devices", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("reservation_count", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("approved_reservation_count", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("completed_reservation_count", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("repair_report_count", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("closed_repair_count", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("utilization_rate", sa.Numeric(5, 2), nullable=False, server_default=sa.text("0.00")),
        sa.Column("avg_repair_hours", sa.Numeric(8, 2), nullable=True),
        *timestamps(),
        sa.UniqueConstraint("metric_date", "period_type", "lab_id", "device_id", name="uk_operation_metrics_scope"),
        sa.CheckConstraint("period_type IN ('daily','weekly','monthly')", name="ck_operation_metrics_period_type"),
        sa.CheckConstraint(
            "total_devices >= 0 AND online_devices >= 0 AND idle_devices >= 0 AND fault_devices >= 0 "
            "AND reservation_count >= 0 AND approved_reservation_count >= 0 "
            "AND completed_reservation_count >= 0 AND repair_report_count >= 0 AND closed_repair_count >= 0",
            name="ck_operation_metrics_counts",
        ),
        sa.CheckConstraint("utilization_rate >= 0 AND utilization_rate <= 100", name="ck_operation_metrics_utilization"),
    )
    for name, columns in {
        "idx_operation_metrics_date_period": ["metric_date", "period_type"],
        "idx_operation_metrics_lab_id": ["lab_id"],
        "idx_operation_metrics_device_id": ["device_id"],
        "idx_operation_metrics_period_lab": ["period_type", "lab_id"],
    }.items():
        op.create_index(name, "operation_metrics", columns)


def downgrade() -> None:
    op.drop_table("operation_metrics")
    op.drop_table("maintenance_records")
    op.drop_table("work_orders")
    op.drop_table("repair_reports")
    op.drop_constraint("ex_reservations_device_time", "reservations", type_="exclude")
    op.drop_table("reservations")
    op.drop_table("devices")
    op.drop_table("device_categories")
    op.drop_table("labs")
    op.drop_table("role_permissions")
    op.drop_table("user_roles")
    op.drop_table("permissions")
    op.drop_table("roles")
    op.drop_table("users")
