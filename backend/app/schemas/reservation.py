from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, Field, model_validator

from app.schemas.common import TimestampMixin


class ReservationStatus(StrEnum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    canceled = "canceled"
    completed = "completed"


class ReservationCreate(BaseModel):
    device_id: UUID
    start_time: datetime
    end_time: datetime
    purpose: str = Field(min_length=1, max_length=1000)

    @model_validator(mode="after")
    def validate_time_range(self) -> "ReservationCreate":
        if self.end_time <= self.start_time:
            raise ValueError("end_time must be later than start_time")
        return self


class ReservationRead(ReservationCreate, TimestampMixin):
    id: UUID
    applicant_id: UUID
    approver_id: UUID | None = None
    status: ReservationStatus = ReservationStatus.pending
    reject_reason: str | None = None


class ReservationCalendarItem(BaseModel):
    id: UUID
    reservation_no: str
    device_id: UUID
    applicant_id: UUID
    start_time: datetime
    end_time: datetime
    purpose: str
    status: ReservationStatus
    title: str


class ReservationAvailabilityRead(BaseModel):
    device_id: UUID
    start_time: datetime
    end_time: datetime
    available: bool
    conflict_count: int
    conflicts: list[ReservationCalendarItem] = Field(default_factory=list)


class ReservationReject(BaseModel):
    reject_reason: str = Field(min_length=1, max_length=1000)
