from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
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


@router.get("", response_model=ApiResponse[PageData[WorkOrderRead]])
def list_work_orders(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    assignee_id: UUID | None = None,
    status: WorkOrderStatus | None = None,
    priority: WorkOrderPriority | None = None,
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
        )
    )


@router.post("", response_model=ApiResponse[WorkOrderRead], status_code=201)
def create_work_order(
    payload: WorkOrderCreate,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ApiResponse[WorkOrderRead]:
    return ok(labops_service.create_work_order(db, payload, current_user.id))


@router.get("/{work_order_id}", response_model=ApiResponse[WorkOrderRead])
def get_work_order(work_order_id: UUID, db: Session = Depends(get_db)) -> ApiResponse[WorkOrderRead]:
    return ok(labops_service.get_work_order(db, work_order_id))


@router.patch("/{work_order_id}/status", response_model=ApiResponse[WorkOrderRead])
def update_work_order_status(
    work_order_id: UUID,
    payload: WorkOrderStatusUpdate,
    db: Session = Depends(get_db),
) -> ApiResponse[WorkOrderRead]:
    return ok(labops_service.update_work_order_status(db, work_order_id, payload.status))


@router.post("/{work_order_id}/finish", response_model=ApiResponse[WorkOrderRead])
def finish_work_order(
    work_order_id: UUID,
    payload: WorkOrderFinish,
    db: Session = Depends(get_db),
) -> ApiResponse[WorkOrderRead]:
    return ok(labops_service.finish_work_order(db, work_order_id, payload.result))
