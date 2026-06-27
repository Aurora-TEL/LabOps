from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel

from app.schemas.common import TimestampMixin


class NotificationCategory(StrEnum):
    info = "info"
    success = "success"
    warning = "warning"
    error = "error"


class NotificationRead(TimestampMixin):
    id: UUID
    recipient_id: UUID | None
    title: str
    content: str
    category: NotificationCategory
    business_type: str | None = None
    business_id: UUID | None = None
    is_read: bool
    read_at: datetime | None = None


class NotificationUnreadSummary(BaseModel):
    unread_count: int


class NotificationMarkRead(BaseModel):
    is_read: bool = True
