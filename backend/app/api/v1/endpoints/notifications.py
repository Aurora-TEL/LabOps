from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user, require_permissions
from app.db.session import get_db
from app.schemas.auth import CurrentUser
from app.schemas.common import ApiResponse, PageData, ok
from app.schemas.notification import NotificationRead, NotificationUnreadSummary
from app.services.notification import notification_audit_service

router = APIRouter()


@router.get("", response_model=ApiResponse[PageData[NotificationRead]])
def list_notifications(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    is_read: bool | None = None,
    current_user: CurrentUser = Depends(require_permissions("notification:view")),
    db: Session = Depends(get_db),
) -> ApiResponse[PageData[NotificationRead]]:
    return ok(
        notification_audit_service.list_notifications(
            db,
            recipient_id=current_user.id,
            page=page,
            page_size=page_size,
            is_read=is_read,
        )
    )


@router.get("/summary", response_model=ApiResponse[NotificationUnreadSummary])
def unread_summary(
    current_user: CurrentUser = Depends(require_permissions("notification:view")),
    db: Session = Depends(get_db),
) -> ApiResponse[NotificationUnreadSummary]:
    return ok(notification_audit_service.unread_summary(db, recipient_id=current_user.id))


@router.patch("/{notification_id}/read", response_model=ApiResponse[NotificationRead])
def mark_notification_read(
    notification_id: UUID,
    current_user: CurrentUser = Depends(require_permissions("notification:update")),
    db: Session = Depends(get_db),
) -> ApiResponse[NotificationRead]:
    notification = notification_audit_service.mark_notification_read(
        db, notification_id=notification_id, recipient_id=current_user.id
    )
    if notification is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="notification not found")
    return ok(notification)


@router.post("/{notification_id}/read", response_model=ApiResponse[NotificationRead])
def mark_notification_read_post(
    notification_id: UUID,
    current_user: CurrentUser = Depends(require_permissions("notification:update")),
    db: Session = Depends(get_db),
) -> ApiResponse[NotificationRead]:
    return mark_notification_read(notification_id, current_user, db)


@router.patch("/read-all", response_model=ApiResponse[dict[str, int]])
def mark_all_notifications_read(
    current_user: CurrentUser = Depends(require_permissions("notification:update")),
    db: Session = Depends(get_db),
) -> ApiResponse[dict[str, int]]:
    updated = notification_audit_service.mark_all_notifications_read(db, recipient_id=current_user.id)
    return ok({"updated": updated})


@router.post("/read-all", response_model=ApiResponse[dict[str, int]])
def mark_all_notifications_read_post(
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ApiResponse[dict[str, int]]:
    if "notification:update" not in current_user.permissions:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="insufficient permission")
    updated = notification_audit_service.mark_all_notifications_read(db, recipient_id=current_user.id)
    return ok({"updated": updated})
