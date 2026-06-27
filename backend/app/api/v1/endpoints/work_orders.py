from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import require_any_permission, require_permissions
from app.db.session import get_db
from app.models import Device, RepairReport, WorkOrder
from app.schemas.auth import CurrentUser
from app.schemas.common import ApiResponse, PageData, ok
from app.schemas.work_order import (
    WorkOrderCreate,
    WorkOrderFinish,
    WorkOrderPriority,
    WorkOrderRead,
    WorkOrderStatus,
    WorkOrderStatusUpdate,
)
from app.services.business import labops_service

router = APIRouter()


def is_device_owner(current_user: CurrentUser) -> bool:
    roles = set(current_user.roles)
    return "device_owner" in roles and not roles.intersection({"lab_admin", "system_admin"})


def ensure_work_order_scope(db: Session, work_order_id: UUID, current_user: CurrentUser) -> None:
    if not is_device_owner(current_user):
        return
    statement = (
        select(WorkOrder.id)
        .join(Device, WorkOrder.device_id == Device.id)
        .where(WorkOrder.id == work_order_id, Device.manager_id == current_user.id)
    )
    if db.scalar(statement) is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="work order is outside owned devices")


def ensure_repair_report_scope(db: Session, repair_report_id: UUID, current_user: CurrentUser) -> None:
    if not is_device_owner(current_user):
        return
    statement = (
        select(RepairReport.id)
        .join(Device, RepairReport.device_id == Device.id)
        .where(RepairReport.id == repair_report_id, Device.manager_id == current_user.id)
    )
    if db.scalar(statement) is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="repair report is outside owned devices")


@router.get("", response_model=ApiResponse[PageData[WorkOrderRead]])
def list_work_orders(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    assignee_id: UUID | None = None,
    status: WorkOrderStatus | None = None,
    priority: WorkOrderPriority | None = None,
    current_user: CurrentUser = Depends(require_any_permission("work_order:update", "work_order:close", "work_order:create")),
    db: Session = Depends(get_db),
) -> ApiResponse[PageData[WorkOrderRead]]:
    return ok(
        labops_service.list_work_orders(
            db,
            page=page,
            page_size=page_size,
            assignee_id=assignee_id,
            status=status,
            priority=priority,
            device_manager_id=current_user.id if is_device_owner(current_user) else None,
        )
    )


@router.post("", response_model=ApiResponse[WorkOrderRead], status_code=201)
def create_work_order(
    payload: WorkOrderCreate,
    current_user: CurrentUser = Depends(require_permissions("work_order:create")),
    db: Session = Depends(get_db),
) -> ApiResponse[WorkOrderRead]:
    ensure_repair_report_scope(db, payload.repair_report_id, current_user)
    return ok(labops_service.create_work_order(db, payload, current_user.id))


@router.get("/{work_order_id}", response_model=ApiResponse[WorkOrderRead])
def get_work_order(
    work_order_id: UUID,
    current_user: CurrentUser = Depends(require_any_permission("work_order:update", "work_order:close", "work_order:create")),
    db: Session = Depends(get_db),
) -> ApiResponse[WorkOrderRead]:
    ensure_work_order_scope(db, work_order_id, current_user)
    return ok(labops_service.get_work_order(db, work_order_id))


@router.patch("/{work_order_id}/status", response_model=ApiResponse[WorkOrderRead])
def update_work_order_status(
    work_order_id: UUID,
    payload: WorkOrderStatusUpdate,
    current_user: CurrentUser = Depends(require_permissions("work_order:update")),
    db: Session = Depends(get_db),
) -> ApiResponse[WorkOrderRead]:
    ensure_work_order_scope(db, work_order_id, current_user)
    return ok(labops_service.update_work_order_status(db, work_order_id, payload.status))


@router.post("/{work_order_id}/finish", response_model=ApiResponse[WorkOrderRead])
def finish_work_order(
    work_order_id: UUID,
    payload: WorkOrderFinish,
    current_user: CurrentUser = Depends(require_permissions("work_order:close")),
    db: Session = Depends(get_db),
) -> ApiResponse[WorkOrderRead]:
    ensure_work_order_scope(db, work_order_id, current_user)
    return ok(labops_service.finish_work_order(db, work_order_id, payload.result))
