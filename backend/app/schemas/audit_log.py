from uuid import UUID

from app.schemas.common import TimestampMixin


class AuditLogRead(TimestampMixin):
    id: UUID
    actor_id: UUID | None = None
    action: str
    resource_type: str
    resource_id: UUID | None = None
    summary: str
    detail: str | None = None
    result: str
