from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class UUIDPrimaryKeyMixin:
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )


class User(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint("status IN ('active','disabled','locked')", name="ck_users_status"),
        Index("idx_users_status", "status"),
        Index("idx_users_real_name", "real_name"),
        Index("uk_users_lower_username", func.lower(text("username")), unique=True),
        Index("uk_users_lower_email", func.lower(text("email")), unique=True, postgresql_where=text("email IS NOT NULL")),
    )

    username: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    real_name: Mapped[str] = mapped_column(String(64), nullable=False)
    email: Mapped[str | None] = mapped_column(String(128), unique=True)
    phone: Mapped[str | None] = mapped_column(String(32))
    department: Mapped[str | None] = mapped_column(String(128))
    student_no: Mapped[str | None] = mapped_column(String(64), unique=True)
    employee_no: Mapped[str | None] = mapped_column(String(64), unique=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, server_default=text("'active'"))
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    roles: Mapped[list[Role]] = relationship(secondary="user_roles", back_populates="users")


class Role(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "roles"

    code: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    is_system: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))

    users: Mapped[list[User]] = relationship(secondary="user_roles", back_populates="roles")
    permissions: Mapped[list[Permission]] = relationship(secondary="role_permissions", back_populates="roles")


class Permission(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "permissions"
    __table_args__ = (Index("idx_permissions_resource_action", "resource", "action"),)

    code: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    resource: Mapped[str] = mapped_column(String(64), nullable=False)
    action: Mapped[str] = mapped_column(String(64), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)

    roles: Mapped[list[Role]] = relationship(secondary="role_permissions", back_populates="permissions")


class UserRole(Base):
    __tablename__ = "user_roles"
    __table_args__ = (Index("idx_user_roles_role_id", "role_id"),)

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    role_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class RolePermission(Base):
    __tablename__ = "role_permissions"
    __table_args__ = (Index("idx_role_permissions_permission_id", "permission_id"),)

    role_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True
    )
    permission_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class Lab(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "labs"
    __table_args__ = (Index("idx_labs_manager_id", "manager_id"), Index("idx_labs_is_active", "is_active"))

    code: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    manager_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    contact_phone: Mapped[str | None] = mapped_column(String(32))
    opening_hours: Mapped[str | None] = mapped_column(String(128))
    description: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))

    devices: Mapped[list[Device]] = relationship(back_populates="lab")


class DeviceCategory(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "device_categories"
    __table_args__ = (
        Index("idx_device_categories_parent_id", "parent_id"),
        Index("idx_device_categories_is_active", "is_active"),
    )

    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("device_categories.id", ondelete="SET NULL")
    )
    code: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))

    devices: Mapped[list[Device]] = relationship(back_populates="category")


class Device(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "devices"
    __table_args__ = (
        CheckConstraint("status IN ('idle','in_use','maintenance','fault','disabled')", name="ck_devices_status"),
        CheckConstraint("health_score >= 0 AND health_score <= 100", name="ck_devices_health_score"),
        CheckConstraint("purchase_price IS NULL OR purchase_price >= 0", name="ck_devices_purchase_price"),
        Index("idx_devices_category_id", "category_id"),
        Index("idx_devices_lab_id", "lab_id"),
        Index("idx_devices_manager_id", "manager_id"),
        Index("idx_devices_status", "status"),
        Index("idx_devices_lab_status", "lab_id", "status"),
        Index("idx_devices_category_status", "category_id", "status"),
    )

    code: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    category_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("device_categories.id", ondelete="RESTRICT"), nullable=False
    )
    lab_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("labs.id", ondelete="RESTRICT"), nullable=False)
    manager_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    status: Mapped[str] = mapped_column(String(32), nullable=False, server_default=text("'idle'"))
    health_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False, server_default=text("100.00"))
    model: Mapped[str | None] = mapped_column(String(128))
    manufacturer: Mapped[str | None] = mapped_column(String(128))
    serial_number: Mapped[str | None] = mapped_column(String(128), unique=True)
    purchase_date: Mapped[date | None] = mapped_column(Date)
    purchase_price: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    location_detail: Mapped[str | None] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)

    category: Mapped[DeviceCategory] = relationship(back_populates="devices")
    lab: Mapped[Lab] = relationship(back_populates="devices")


class Reservation(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "reservations"
    __table_args__ = (
        CheckConstraint("status IN ('pending','approved','rejected','cancelled','completed')", name="ck_reservations_status"),
        CheckConstraint("start_time < end_time", name="ck_reservations_time_range"),
        CheckConstraint("participant_count > 0", name="ck_reservations_participant_count"),
        Index("idx_reservations_device_time", "device_id", "start_time", "end_time"),
        Index("idx_reservations_applicant_id", "applicant_id"),
        Index("idx_reservations_approver_id", "approver_id"),
        Index("idx_reservations_status", "status"),
        Index("idx_reservations_start_time", "start_time"),
        Index("idx_reservations_device_status", "device_id", "status"),
    )

    reservation_no: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    device_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("devices.id", ondelete="RESTRICT"), nullable=False)
    applicant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    approver_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    purpose: Mapped[str] = mapped_column(Text, nullable=False)
    participant_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("1"))
    status: Mapped[str] = mapped_column(String(32), nullable=False, server_default=text("'pending'"))
    reject_reason: Mapped[str | None] = mapped_column(Text)
    cancel_reason: Mapped[str | None] = mapped_column(Text)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    remark: Mapped[str | None] = mapped_column(Text)


class RepairReport(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "repair_reports"
    __table_args__ = (
        CheckConstraint("status IN ('submitted','accepted','assigned','processing','finished','closed')", name="ck_repair_reports_status"),
        CheckConstraint("urgency IN ('low','medium','high','urgent')", name="ck_repair_reports_urgency"),
        Index("idx_repair_reports_device_id", "device_id"),
        Index("idx_repair_reports_reporter_id", "reporter_id"),
        Index("idx_repair_reports_status", "status"),
        Index("idx_repair_reports_fault_type", "fault_type"),
        Index("idx_repair_reports_created_at", "created_at"),
        Index("idx_repair_reports_device_status", "device_id", "status"),
    )

    report_no: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    device_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("devices.id", ondelete="RESTRICT"), nullable=False)
    reporter_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    accepted_by_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    fault_type: Mapped[str] = mapped_column(String(64), nullable=False)
    urgency: Mapped[str] = mapped_column(String(32), nullable=False, server_default=text("'medium'"))
    description: Mapped[str] = mapped_column(Text, nullable=False)
    image_url: Mapped[str | None] = mapped_column(String(512))
    status: Mapped[str] = mapped_column(String(32), nullable=False, server_default=text("'submitted'"))
    accepted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    close_note: Mapped[str | None] = mapped_column(Text)


class WorkOrder(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "work_orders"
    __table_args__ = (
        CheckConstraint("priority IN ('low','medium','high','urgent')", name="ck_work_orders_priority"),
        CheckConstraint("status IN ('assigned','processing','finished','closed')", name="ck_work_orders_status"),
        CheckConstraint(
            "planned_start_at IS NULL OR planned_end_at IS NULL OR planned_start_at < planned_end_at",
            name="ck_work_orders_planned_range",
        ),
        CheckConstraint("cost_amount IS NULL OR cost_amount >= 0", name="ck_work_orders_cost_amount"),
        Index("idx_work_orders_repair_report_id", "repair_report_id"),
        Index("idx_work_orders_device_id", "device_id"),
        Index("idx_work_orders_assignee_id", "assignee_id"),
        Index("idx_work_orders_status", "status"),
        Index("idx_work_orders_priority", "priority"),
        Index("idx_work_orders_created_at", "created_at"),
        Index("idx_work_orders_device_status", "device_id", "status"),
    )

    work_order_no: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    repair_report_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("repair_reports.id", ondelete="RESTRICT"), nullable=False
    )
    device_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("devices.id", ondelete="RESTRICT"), nullable=False)
    creator_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    assignee_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    priority: Mapped[str] = mapped_column(String(32), nullable=False, server_default=text("'medium'"))
    status: Mapped[str] = mapped_column(String(32), nullable=False, server_default=text("'assigned'"))
    planned_start_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    planned_end_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    process_note: Mapped[str | None] = mapped_column(Text)
    result: Mapped[str | None] = mapped_column(Text)
    cost_amount: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))


class MaintenanceRecord(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "maintenance_records"
    __table_args__ = (
        CheckConstraint(
            "maintenance_type IN ('routine','repair','calibration','replacement','enable','disable')",
            name="ck_maintenance_records_type",
        ),
        CheckConstraint("cost_amount IS NULL OR cost_amount >= 0", name="ck_maintenance_records_cost_amount"),
        Index("idx_maintenance_records_device_id", "device_id"),
        Index("idx_maintenance_records_work_order_id", "work_order_id"),
        Index("idx_maintenance_records_maintainer_id", "maintainer_id"),
        Index("idx_maintenance_records_type", "maintenance_type"),
        Index("idx_maintenance_records_maintained_at", "maintained_at"),
        Index("idx_maintenance_records_device_time", "device_id", "maintained_at"),
    )

    device_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("devices.id", ondelete="RESTRICT"), nullable=False)
    work_order_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("work_orders.id", ondelete="SET NULL"))
    maintainer_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    maintenance_type: Mapped[str] = mapped_column(String(32), nullable=False)
    title: Mapped[str] = mapped_column(String(128), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    result: Mapped[str | None] = mapped_column(Text)
    cost_amount: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    maintained_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    next_maintenance_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class Notification(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "notifications"
    __table_args__ = (
        CheckConstraint("category IN ('info','success','warning','error')", name="ck_notifications_category"),
        Index("idx_notifications_recipient_id", "recipient_id"),
        Index("idx_notifications_is_read", "is_read"),
        Index("idx_notifications_business", "business_type", "business_id"),
        Index("idx_notifications_recipient_read_created", "recipient_id", "is_read", "created_at"),
    )

    recipient_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True
    )
    title: Mapped[str] = mapped_column(String(128), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(32), nullable=False, server_default=text("'info'"))
    business_type: Mapped[str | None] = mapped_column(String(64))
    business_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    is_read: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class AuditLog(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "audit_logs"
    __table_args__ = (
        CheckConstraint("result IN ('success','failure')", name="ck_audit_logs_result"),
        Index("idx_audit_logs_actor_id", "actor_id"),
        Index("idx_audit_logs_resource", "resource_type", "resource_id"),
        Index("idx_audit_logs_action", "action"),
        Index("idx_audit_logs_created_at", "created_at"),
    )

    actor_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    action: Mapped[str] = mapped_column(String(64), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(64), nullable=False)
    resource_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    summary: Mapped[str] = mapped_column(String(255), nullable=False)
    detail: Mapped[str | None] = mapped_column(Text)
    result: Mapped[str] = mapped_column(String(32), nullable=False, server_default=text("'success'"))


class OperationMetric(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "operation_metrics"
    __table_args__ = (
        UniqueConstraint("metric_date", "period_type", "lab_id", "device_id", name="uk_operation_metrics_scope"),
        CheckConstraint("period_type IN ('daily','weekly','monthly')", name="ck_operation_metrics_period_type"),
        CheckConstraint(
            "total_devices >= 0 AND online_devices >= 0 AND idle_devices >= 0 AND fault_devices >= 0 "
            "AND reservation_count >= 0 AND approved_reservation_count >= 0 "
            "AND completed_reservation_count >= 0 AND repair_report_count >= 0 AND closed_repair_count >= 0",
            name="ck_operation_metrics_counts",
        ),
        CheckConstraint("utilization_rate >= 0 AND utilization_rate <= 100", name="ck_operation_metrics_utilization"),
        Index("idx_operation_metrics_date_period", "metric_date", "period_type"),
        Index("idx_operation_metrics_lab_id", "lab_id"),
        Index("idx_operation_metrics_device_id", "device_id"),
        Index("idx_operation_metrics_period_lab", "period_type", "lab_id"),
    )

    metric_date: Mapped[date] = mapped_column(Date, nullable=False)
    period_type: Mapped[str] = mapped_column(String(32), nullable=False)
    lab_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("labs.id", ondelete="SET NULL"))
    device_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("devices.id", ondelete="SET NULL"))
    total_devices: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    online_devices: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    idle_devices: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    fault_devices: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    reservation_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    approved_reservation_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    completed_reservation_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    repair_report_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    closed_repair_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    utilization_rate: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False, server_default=text("0.00"))
    avg_repair_hours: Mapped[Decimal | None] = mapped_column(Numeric(8, 2))
