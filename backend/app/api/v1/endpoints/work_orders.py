from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.common import ApiResponse, PageData, ok, utc_now
from app.schemas.work_order import (
    WorkOrderCreate,
    WorkOrderFinish,
    WorkOrderPriority,
    WorkOrderRead,
    WorkOrderStatus,
    WorkOrderStatusUpdate,
)

router = APIRouter()

DEMO_WORK_ORDER_ID = UUID("40000000-0000-0000-0000-000000000001")
DEMO_REPAIR_REPORT_ID = UUID("30000000-0000-0000-0000-000000000001")


def demo_work_order(work_order_id: UUID = DEMO_WORK_ORDER_ID) -> WorkOrderRead:
    now = utc_now()
    return WorkOrderRead(
        id=work_order_id,
        repair_report_id=DEMO_REPAIR_REPORT_ID,
        assignee_id=UUID("00000000-0000-0000-0000-000000000001"),
        priority=WorkOrderPriority.high,
        status=WorkOrderStatus.pending,
        result=None,
        started_at=None,
        finished_at=None,
        created_at=now,
        updated_at=now,
    )


@router.get("", response_model=ApiResponse[PageData[WorkOrderRead]])
def list_work_orders(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    assignee_id: UUID | None = None,
    status: WorkOrderStatus | None = None,
    priority: WorkOrderPriority | None = None,
    db: Session = Depends(get_db),
) -> ApiResponse[PageData[WorkOrderRead]]:
    _ = (assignee_id, status, priority, db)
    return ok(PageData(items=[demo_work_order()], page=page, page_size=page_size, total=1))


@router.post("", response_model=ApiResponse[WorkOrderRead], status_code=201)
def create_work_order(payload: WorkOrderCreate, db: Session = Depends(get_db)) -> ApiResponse[WorkOrderRead]:
    _ = db
    now = utc_now()
    return ok(
        WorkOrderRead(
            id=DEMO_WORK_ORDER_ID,
            status=WorkOrderStatus.pending,
            result=None,
            started_at=None,
            finished_at=None,
            created_at=now,
            updated_at=now,
            **payload.model_dump(),
        )
    )


@router.get("/{work_order_id}", response_model=ApiResponse[WorkOrderRead])
def get_work_order(work_order_id: UUID, db: Session = Depends(get_db)) -> ApiResponse[WorkOrderRead]:
    _ = db
    return ok(demo_work_order(work_order_id))


@router.patch("/{work_order_id}/status", response_model=ApiResponse[WorkOrderRead])
def update_work_order_status(
    work_order_id: UUID,
    payload: WorkOrderStatusUpdate,
    db: Session = Depends(get_db),
) -> ApiResponse[WorkOrderRead]:
    _ = db
    started_at = utc_now() if payload.status == WorkOrderStatus.processing else None
    return ok(demo_work_order(work_order_id).model_copy(update={"status": payload.status, "started_at": started_at, "updated_at": utc_now()}))


@router.post("/{work_order_id}/finish", response_model=ApiResponse[WorkOrderRead])
def finish_work_order(
    work_order_id: UUID,
    payload: WorkOrderFinish,
    db: Session = Depends(get_db),
) -> ApiResponse[WorkOrderRead]:
    _ = db
    now = utc_now()
    return ok(
        demo_work_order(work_order_id).model_copy(
            update={
                "status": WorkOrderStatus.finished,
                "result": payload.result,
                "finished_at": now,
                "updated_at": now,
            }
        )
    )
