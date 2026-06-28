from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import TimestampMixin


class MaintenanceType(StrEnum):
    routine = "routine"
    repair = "repair"
    calibration = "calibration"
    replacement = "replacement"
    enable = "enable"
    disable = "disable"


class MaintenanceRecordCreate(BaseModel):
    device_id: UUID
    work_order_id: UUID | None = None
    maintenance_type: MaintenanceType = MaintenanceType.routine
    title: str = Field(min_length=1, max_length=128)
    content: str = Field(min_length=1, max_length=2000)
    result: str | None = Field(default=None, max_length=2000)
    cost_amount: Decimal | None = Field(default=None, ge=0)
    maintained_at: datetime | None = None
    next_maintenance_at: datetime | None = None


class MaintenanceRecordRead(TimestampMixin):
    id: UUID
    device_id: UUID
    work_order_id: UUID | None = None
    maintainer_id: UUID | None = None
    maintenance_type: MaintenanceType
    title: str
    content: str
    result: str | None = None
    cost_amount: Decimal | None = None
    maintained_at: datetime
    next_maintenance_at: datetime | None = None
