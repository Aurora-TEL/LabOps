from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.security import require_permissions
from app.db.session import get_db
from app.schemas.audit_log import AuditLogRead
from app.schemas.auth import CurrentUser
from app.schemas.common import ApiResponse, PageData, ok
from app.services.notification import notification_audit_service

router = APIRouter()


@router.get("", response_model=ApiResponse[PageData[AuditLogRead]])
def list_audit_logs(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    actor_id: UUID | None = None,
    resource_type: str | None = Query(default=None, max_length=64),
    action: str | None = Query(default=None, max_length=64),
    current_user: CurrentUser = Depends(require_permissions("audit_log:view")),
    db: Session = Depends(get_db),
) -> ApiResponse[PageData[AuditLogRead]]:
    _ = current_user
    return ok(
        notification_audit_service.list_audit_logs(
            db,
            page=page,
            page_size=page_size,
            actor_id=actor_id,
            resource_type=resource_type,
            action=action,
        )
    )
