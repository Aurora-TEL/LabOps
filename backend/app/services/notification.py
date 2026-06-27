from __future__ import annotations

from collections.abc import Iterable
from uuid import UUID

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.models import AuditLog, Device, Notification, Role, User
from app.schemas.audit_log import AuditLogRead
from app.schemas.common import PageData, utc_now
from app.schemas.notification import NotificationRead, NotificationUnreadSummary


class NotificationAuditService:
    def notify_users(
        self,
        db: Session,
        recipient_ids: Iterable[UUID | None],
        *,
        title: str,
        content: str,
        category: str = "info",
        business_type: str | None = None,
        business_id: UUID | None = None,
    ) -> None:
        seen: set[UUID] = set()
        for recipient_id in recipient_ids:
            if recipient_id is None or recipient_id in seen:
                continue
            seen.add(recipient_id)
            db.add(
                Notification(
                    recipient_id=recipient_id,
                    title=title,
                    content=content,
                    category=category,
                    business_type=business_type,
                    business_id=business_id,
                )
            )

    def notify_device_manager(
        self,
        db: Session,
        device_id: UUID,
        *,
        title: str,
        content: str,
        category: str = "info",
        business_type: str | None = None,
        business_id: UUID | None = None,
    ) -> None:
        manager_id = db.scalar(select(Device.manager_id).where(Device.id == device_id))
        self.notify_users(
            db,
            [manager_id],
            title=title,
            content=content,
            category=category,
            business_type=business_type,
            business_id=business_id,
        )

    def notify_admins(
        self,
        db: Session,
        *,
        title: str,
        content: str,
        category: str = "info",
        business_type: str | None = None,
        business_id: UUID | None = None,
    ) -> None:
        self.notify_users(
            db,
            self._admin_user_ids(db),
            title=title,
            content=content,
            category=category,
            business_type=business_type,
            business_id=business_id,
        )

    def audit(
        self,
        db: Session,
        *,
        action: str,
        resource_type: str,
        resource_id: UUID | None,
        actor_id: UUID | None,
        summary: str,
        detail: str | None = None,
        result: str = "success",
    ) -> None:
        db.add(
            AuditLog(
                actor_id=actor_id,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                summary=summary,
                detail=detail,
                result=result,
            )
        )

    def list_notifications(
        self,
        db: Session,
        *,
        recipient_id: UUID,
        page: int,
        page_size: int,
        is_read: bool | None = None,
    ) -> PageData[NotificationRead]:
        statement = select(Notification).where(Notification.recipient_id == recipient_id)
        if is_read is not None:
            statement = statement.where(Notification.is_read == is_read)
        statement = statement.order_by(Notification.created_at.desc())
        page_data = self._page(db, statement, page, page_size)
        return PageData(
            items=[self._notification_read(item) for item in page_data.items],
            page=page_data.page,
            page_size=page_data.page_size,
            total=page_data.total,
        )

    def unread_summary(self, db: Session, *, recipient_id: UUID) -> NotificationUnreadSummary:
        unread_count = (
            db.scalar(
                select(func.count())
                .select_from(Notification)
                .where(Notification.recipient_id == recipient_id, Notification.is_read.is_(False))
            )
            or 0
        )
        return NotificationUnreadSummary(unread_count=unread_count)

    def mark_notification_read(self, db: Session, *, notification_id: UUID, recipient_id: UUID) -> NotificationRead | None:
        notification = db.get(Notification, notification_id)
        if notification is None or notification.recipient_id != recipient_id:
            return None
        notification.is_read = True
        notification.read_at = notification.read_at or utc_now()
        db.commit()
        db.refresh(notification)
        return self._notification_read(notification)

    def mark_all_notifications_read(self, db: Session, *, recipient_id: UUID) -> int:
        notifications = list(
            db.scalars(
                select(Notification).where(Notification.recipient_id == recipient_id, Notification.is_read.is_(False))
            )
        )
        for notification in notifications:
            notification.is_read = True
            notification.read_at = notification.read_at or utc_now()
        db.commit()
        return len(notifications)

    def list_audit_logs(
        self,
        db: Session,
        *,
        page: int,
        page_size: int,
        actor_id: UUID | None = None,
        resource_type: str | None = None,
        action: str | None = None,
    ) -> PageData[AuditLogRead]:
        statement = select(AuditLog)
        if actor_id is not None:
            statement = statement.where(AuditLog.actor_id == actor_id)
        if resource_type:
            statement = statement.where(AuditLog.resource_type == resource_type)
        if action:
            statement = statement.where(AuditLog.action == action)
        statement = statement.order_by(AuditLog.created_at.desc())
        page_data = self._page(db, statement, page, page_size)
        return PageData(
            items=[self._audit_log_read(item) for item in page_data.items],
            page=page_data.page,
            page_size=page_data.page_size,
            total=page_data.total,
        )

    @staticmethod
    def _admin_user_ids(db: Session) -> list[UUID]:
        return list(
            db.scalars(select(User.id).join(User.roles).where(Role.code.in_(["lab_admin", "system_admin"])).distinct())
        )

    @staticmethod
    def _page(db: Session, statement: Select[tuple[object]], page: int, page_size: int) -> PageData:
        total_statement = select(func.count()).select_from(statement.order_by(None).subquery())
        total = db.scalar(total_statement) or 0
        items = db.scalars(statement.offset((page - 1) * page_size).limit(page_size)).all()
        return PageData(items=items, page=page, page_size=page_size, total=total)

    @staticmethod
    def _notification_read(notification: Notification) -> NotificationRead:
        return NotificationRead(
            id=notification.id,
            recipient_id=notification.recipient_id,
            title=notification.title,
            content=notification.content,
            category=notification.category,
            business_type=notification.business_type,
            business_id=notification.business_id,
            is_read=notification.is_read,
            read_at=notification.read_at,
            created_at=notification.created_at,
            updated_at=notification.updated_at,
        )

    @staticmethod
    def _audit_log_read(log: AuditLog) -> AuditLogRead:
        return AuditLogRead(
            id=log.id,
            actor_id=log.actor_id,
            action=log.action,
            resource_type=log.resource_type,
            resource_id=log.resource_id,
            summary=log.summary,
            detail=log.detail,
            result=log.result,
            created_at=log.created_at,
            updated_at=log.updated_at,
        )


notification_audit_service = NotificationAuditService()
