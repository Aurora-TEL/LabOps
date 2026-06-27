from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import TimestampMixin


class WorkOrderPriority(StrEnum):
    low = "low"
    medium = "medium"
    high = "high"
    urgent = "urgent"


class WorkOrderStatus(StrEnum):
    pending = "pending"
    assigned = "assigned"
    processing = "processing"
    finished = "finished"
    canceled = "canceled"
    closed = "closed"


class WorkOrderCreate(BaseModel):
    repair_report_id: UUID
    assignee_id: UUID | None = None
    priority: WorkOrderPriority = WorkOrderPriority.medium


class WorkOrderStatusUpdate(BaseModel):
    status: WorkOrderStatus


class WorkOrderFinish(BaseModel):
    result: str = Field(min_length=1, max_length=2000)


class WorkOrderRead(WorkOrderCreate, TimestampMixin):
    id: UUID
    status: WorkOrderStatus = WorkOrderStatus.pending
    result: str | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None
