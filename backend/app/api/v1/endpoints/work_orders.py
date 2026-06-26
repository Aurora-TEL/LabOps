from uuid import UUID

from fastapi import APIRouter, Query

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
) -> ApiResponse[PageData[WorkOrderRead]]:
    return ok(
        labops_service.list_work_orders(
            page=page,
            page_size=page_size,
            assignee_id=assignee_id,
            status=status,
            priority=priority,
        )
    )


@router.post("", response_model=ApiResponse[WorkOrderRead], status_code=201)
def create_work_order(payload: WorkOrderCreate) -> ApiResponse[WorkOrderRead]:
    return ok(labops_service.create_work_order(payload))


@router.get("/{work_order_id}", response_model=ApiResponse[WorkOrderRead])
def get_work_order(work_order_id: UUID) -> ApiResponse[WorkOrderRead]:
    return ok(labops_service.get_work_order(work_order_id))


@router.patch("/{work_order_id}/status", response_model=ApiResponse[WorkOrderRead])
def update_work_order_status(work_order_id: UUID, payload: WorkOrderStatusUpdate) -> ApiResponse[WorkOrderRead]:
    return ok(labops_service.update_work_order_status(work_order_id, payload.status))


@router.post("/{work_order_id}/finish", response_model=ApiResponse[WorkOrderRead])
def finish_work_order(work_order_id: UUID, payload: WorkOrderFinish) -> ApiResponse[WorkOrderRead]:
    return ok(labops_service.finish_work_order(work_order_id, payload.result))
