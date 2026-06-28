from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import Select, func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.models import AuditLog, Permission, Role, User
from app.schemas.common import PageData
from app.schemas.system import ManagedUserRead, PermissionRead, RoleRead, SystemManagementSummary, UserStatus
from app.services.notification import notification_audit_service


def _not_found(resource: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{resource} not found")


def _bad_request(message: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)


def _conflict(message: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=message)


def _page(db: Session, statement: Select[tuple[object]], page: int, page_size: int) -> PageData:
    total_statement = select(func.count()).select_from(statement.order_by(None).subquery())
    total = db.scalar(total_statement) or 0
    items = db.scalars(statement.offset((page - 1) * page_size).limit(page_size)).all()
    return PageData(items=items, page=page, page_size=page_size, total=total)


class SystemManagementService:
    def summary(self, db: Session) -> SystemManagementSummary:
        return SystemManagementSummary(
            user_total=db.scalar(select(func.count()).select_from(User)) or 0,
            active_users=db.scalar(select(func.count()).select_from(User).where(User.status == "active")) or 0,
            disabled_users=db.scalar(select(func.count()).select_from(User).where(User.status == "disabled")) or 0,
            role_total=db.scalar(select(func.count()).select_from(Role)) or 0,
            permission_total=db.scalar(select(func.count()).select_from(Permission)) or 0,
        )

    def list_users(
        self,
        db: Session,
        *,
        page: int,
        page_size: int,
        keyword: str | None = None,
        status_: UserStatus | None = None,
        role_code: str | None = None,
    ) -> PageData[ManagedUserRead]:
        statement = select(User).options(selectinload(User.roles).selectinload(Role.permissions))
        if keyword:
            pattern = f"%{keyword.lower().strip()}%"
            statement = statement.where(
                or_(
                    func.lower(User.username).like(pattern),
                    func.lower(User.real_name).like(pattern),
                    func.lower(User.department).like(pattern),
                )
            )
        if status_ is not None:
            statement = statement.where(User.status == status_.value)
        if role_code:
            statement = statement.join(User.roles).where(Role.code == role_code)
        statement = statement.order_by(User.created_at.asc())
        page_data = _page(db, statement, page, page_size)
        return PageData(
            items=[self._user_read(item) for item in page_data.items],
            page=page_data.page,
            page_size=page_data.page_size,
            total=page_data.total,
        )

    def list_roles(self, db: Session) -> list[RoleRead]:
        roles = db.scalars(select(Role).options(selectinload(Role.permissions), selectinload(Role.users)).order_by(Role.code.asc())).all()
        return [self._role_read(role) for role in roles]

    def list_permissions(self, db: Session) -> list[PermissionRead]:
        permissions = db.scalars(select(Permission).order_by(Permission.resource.asc(), Permission.action.asc())).all()
        return [self._permission_read(permission) for permission in permissions]

    def update_user_status(self, db: Session, *, user_id: UUID, status_: UserStatus, actor_id: UUID) -> ManagedUserRead:
        user = self._user(db, user_id)
        if user.id == actor_id and status_ != UserStatus.active:
            raise _bad_request("current user cannot disable or lock self")
        if user.status == "active" and status_ != UserStatus.active and self._is_last_active_system_admin(db, user):
            raise _bad_request("last active system admin cannot be disabled")
        user.status = status_.value
        notification_audit_service.audit(
            db,
            action="user.update_status",
            resource_type="user",
            resource_id=user.id,
            actor_id=actor_id,
            summary=f"Update user {user.username} status to {status_.value}",
        )
        self._commit(db)
        db.refresh(user)
        return self._user_read(self._user(db, user_id))

    def update_user_roles(self, db: Session, *, user_id: UUID, role_codes: list[str], actor_id: UUID) -> ManagedUserRead:
        user = self._user(db, user_id)
        unique_codes = sorted(set(role_codes))
        roles = list(db.scalars(select(Role).where(Role.code.in_(unique_codes)).options(selectinload(Role.permissions))))
        found_codes = {role.code for role in roles}
        missing_codes = sorted(set(unique_codes) - found_codes)
        if missing_codes:
            raise _bad_request(f"unknown roles: {', '.join(missing_codes)}")
        if any(role.code == "system_admin" for role in user.roles) and "system_admin" not in found_codes:
            if self._is_last_active_system_admin(db, user):
                raise _bad_request("last active system admin role cannot be removed")
        user.roles = roles
        notification_audit_service.audit(
            db,
            action="user.update_roles",
            resource_type="user",
            resource_id=user.id,
            actor_id=actor_id,
            summary=f"Update user {user.username} roles",
            detail=", ".join(unique_codes),
        )
        self._commit(db)
        db.refresh(user)
        return self._user_read(self._user(db, user_id))

    @staticmethod
    def _user(db: Session, user_id: UUID) -> User:
        user = db.get(User, user_id, options=[selectinload(User.roles).selectinload(Role.permissions)])
        if user is None:
            raise _not_found("user")
        return user

    @staticmethod
    def _is_last_active_system_admin(db: Session, user: User) -> bool:
        is_system_admin = any(role.code == "system_admin" for role in user.roles)
        if not is_system_admin:
            return False
        active_admin_count = (
            db.scalar(
                select(func.count())
                .select_from(User)
                .join(User.roles)
                .where(User.status == "active", Role.code == "system_admin")
            )
            or 0
        )
        return active_admin_count <= 1

    @staticmethod
    def _commit(db: Session) -> None:
        try:
            db.commit()
        except IntegrityError as exc:
            db.rollback()
            raise _conflict("request conflicts with existing data") from exc

    @staticmethod
    def _permission_read(permission: Permission) -> PermissionRead:
        return PermissionRead(
            id=permission.id,
            code=permission.code,
            name=permission.name,
            resource=permission.resource,
            action=permission.action,
            description=permission.description,
        )

    def _role_read(self, role: Role) -> RoleRead:
        return RoleRead(
            id=role.id,
            code=role.code,
            name=role.name,
            description=role.description,
            is_system=role.is_system,
            permissions=[self._permission_read(permission) for permission in sorted(role.permissions, key=lambda item: item.code)],
            user_count=len(role.users),
            created_at=role.created_at,
            updated_at=role.updated_at,
        )

    def _user_read(self, user: User) -> ManagedUserRead:
        return ManagedUserRead(
            id=user.id,
            username=user.username,
            real_name=user.real_name,
            email=user.email,
            phone=user.phone,
            department=user.department,
            student_no=user.student_no,
            employee_no=user.employee_no,
            status=UserStatus(user.status),
            last_login_at=user.last_login_at,
            roles=[self._role_read(role) for role in sorted(user.roles, key=lambda item: item.code)],
            created_at=user.created_at,
            updated_at=user.updated_at,
        )


system_management_service = SystemManagementService()
