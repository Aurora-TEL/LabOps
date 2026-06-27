from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import TimestampMixin


class RepairReportStatus(StrEnum):
    submitted = "submitted"
    accepted = "accepted"
    assigned = "assigned"
    processing = "processing"
    finished = "finished"
    closed = "closed"


class RepairReportCreate(BaseModel):
    device_id: UUID
    fault_type: str = Field(min_length=1, max_length=64)
    description: str = Field(min_length=1, max_length=2000)


class RepairReportRead(RepairReportCreate, TimestampMixin):
    id: UUID
    reporter_id: UUID
    status: RepairReportStatus = RepairReportStatus.submitted
