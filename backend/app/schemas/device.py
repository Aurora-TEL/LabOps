from datetime import date
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import TimestampMixin


class DeviceStatus(StrEnum):
    available = "available"
    reserved = "reserved"
    in_use = "in_use"
    maintenance = "maintenance"
    disabled = "disabled"


class DeviceBase(BaseModel):
    code: str = Field(min_length=1, max_length=64)
    name: str = Field(min_length=1, max_length=128)
    category_id: UUID | None = None
    lab_id: UUID | None = None
    manager_id: UUID | None = None
    status: DeviceStatus = DeviceStatus.available
    health_score: float | None = Field(default=None, ge=0, le=100)
    purchase_date: date | None = None


class DeviceCreate(DeviceBase):
    pass


class DeviceUpdate(BaseModel):
    code: str | None = Field(default=None, min_length=1, max_length=64)
    name: str | None = Field(default=None, min_length=1, max_length=128)
    category_id: UUID | None = None
    lab_id: UUID | None = None
    manager_id: UUID | None = None
    status: DeviceStatus | None = None
    health_score: float | None = Field(default=None, ge=0, le=100)
    purchase_date: date | None = None


class DeviceStatusUpdate(BaseModel):
    status: DeviceStatus
    reason: str | None = Field(default=None, max_length=255)


class DeviceRead(DeviceBase, TimestampMixin):
    id: UUID
