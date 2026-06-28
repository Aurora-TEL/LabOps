from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.security import require_any_permission, require_permissions
from app.db.session import get_db
from app.schemas.auth import CurrentUser
from app.schemas.common import ApiResponse, PageData, ok
from app.schemas.system import ManagedUserRead, PermissionRead, RoleRead, SystemManagementSummary, UserRoleUpdate, UserStatus, UserStatusUpdate
from app.services.system_management import system_management_service

router = APIRouter()


@router.get("/summary", response_model=ApiResponse[SystemManagementSummary])
def system_summary(
    current_user: CurrentUser = Depends(require_any_permission("user:manage", "role:manage")),
    db: Session = Depends(get_db),
) -> ApiResponse[SystemManagementSummary]:
    _ = current_user
    return ok(system_management_service.summary(db))


@router.get("/users", response_model=ApiResponse[PageData[ManagedUserRead]])
def list_users(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    keyword: str | None = Query(default=None, max_length=64),
    status: UserStatus | None = None,
    role_code: str | None = Query(default=None, max_length=64),
    current_user: CurrentUser = Depends(require_permissions("user:manage")),
    db: Session = Depends(get_db),
) -> ApiResponse[PageData[ManagedUserRead]]:
    _ = current_user
    return ok(
        system_management_service.list_users(
            db,
            page=page,
            page_size=page_size,
            keyword=keyword,
            status_=status,
            role_code=role_code,
        )
    )


@router.patch("/users/{user_id}/status", response_model=ApiResponse[ManagedUserRead])
def update_user_status(
    user_id: UUID,
    payload: UserStatusUpdate,
    current_user: CurrentUser = Depends(require_permissions("user:manage")),
    db: Session = Depends(get_db),
) -> ApiResponse[ManagedUserRead]:
    return ok(system_management_service.update_user_status(db, user_id=user_id, status_=payload.status, actor_id=current_user.id))


@router.put("/users/{user_id}/roles", response_model=ApiResponse[ManagedUserRead])
def update_user_roles(
    user_id: UUID,
    payload: UserRoleUpdate,
    current_user: CurrentUser = Depends(require_permissions("role:manage")),
    db: Session = Depends(get_db),
) -> ApiResponse[ManagedUserRead]:
    return ok(system_management_service.update_user_roles(db, user_id=user_id, role_codes=payload.role_codes, actor_id=current_user.id))


@router.get("/roles", response_model=ApiResponse[list[RoleRead]])
def list_roles(
    current_user: CurrentUser = Depends(require_permissions("role:manage")),
    db: Session = Depends(get_db),
) -> ApiResponse[list[RoleRead]]:
    _ = current_user
    return ok(system_management_service.list_roles(db))


@router.get("/permissions", response_model=ApiResponse[list[PermissionRead]])
def list_permissions(
    current_user: CurrentUser = Depends(require_permissions("role:manage")),
    db: Session = Depends(get_db),
) -> ApiResponse[list[PermissionRead]]:
    _ = current_user
    return ok(system_management_service.list_permissions(db))
