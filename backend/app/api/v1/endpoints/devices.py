from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import require_permissions
from app.db.session import get_db
from app.models import Device
from app.schemas.auth import CurrentUser
from app.schemas.common import ApiResponse, PageData, ok
from app.schemas.device import DeviceCreate, DeviceRead, DeviceStatus, DeviceStatusUpdate, DeviceUpdate
from app.services.business import labops_service

router = APIRouter()


def scoped_manager_id(current_user: CurrentUser) -> UUID | None:
    roles = set(current_user.roles)
    if "device_owner" in roles and not roles.intersection({"lab_admin", "system_admin"}):
        return current_user.id
    return None


def ensure_device_scope(db: Session, device_id: UUID, current_user: CurrentUser) -> None:
    manager_id = scoped_manager_id(current_user)
    if manager_id is None:
        return
    if db.scalar(select(Device.id).where(Device.id == device_id, Device.manager_id == manager_id)) is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="device is outside owned devices")


@router.get("", response_model=ApiResponse[PageData[DeviceRead]])
def list_devices(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    keyword: str | None = Query(default=None, max_length=128),
    lab_id: UUID | None = None,
    category_id: UUID | None = None,
    status: DeviceStatus | None = None,
    current_user: CurrentUser = Depends(require_permissions("device:view")),
    db: Session = Depends(get_db),
) -> ApiResponse[PageData[DeviceRead]]:
    return ok(
        labops_service.list_devices(
            db,
            page=page,
            page_size=page_size,
            keyword=keyword,
            lab_id=lab_id,
            category_id=category_id,
            status=status,
            manager_id=scoped_manager_id(current_user),
        )
    )


@router.post("", response_model=ApiResponse[DeviceRead], status_code=201)
def create_device(
    payload: DeviceCreate,
    current_user: CurrentUser = Depends(require_permissions("device:create")),
    db: Session = Depends(get_db),
) -> ApiResponse[DeviceRead]:
    _ = current_user
    return ok(labops_service.create_device(db, payload))


@router.get("/{device_id}", response_model=ApiResponse[DeviceRead])
def get_device(
    device_id: UUID,
    current_user: CurrentUser = Depends(require_permissions("device:view")),
    db: Session = Depends(get_db),
) -> ApiResponse[DeviceRead]:
    ensure_device_scope(db, device_id, current_user)
    return ok(labops_service.get_device(db, device_id))


@router.put("/{device_id}", response_model=ApiResponse[DeviceRead])
def update_device(
    device_id: UUID,
    payload: DeviceUpdate,
    current_user: CurrentUser = Depends(require_permissions("device:update")),
    db: Session = Depends(get_db),
) -> ApiResponse[DeviceRead]:
    ensure_device_scope(db, device_id, current_user)
    if scoped_manager_id(current_user) is not None and "manager_id" in payload.model_fields_set:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="device owner cannot change manager")
    return ok(labops_service.update_device(db, device_id, payload))


@router.patch("/{device_id}/status", response_model=ApiResponse[DeviceRead])
def update_device_status(
    device_id: UUID,
    payload: DeviceStatusUpdate,
    current_user: CurrentUser = Depends(require_permissions("device:update")),
    db: Session = Depends(get_db),
) -> ApiResponse[DeviceRead]:
    ensure_device_scope(db, device_id, current_user)
    _ = payload.reason
    return ok(labops_service.update_device_status(db, device_id, payload.status))


@router.delete("/{device_id}", response_model=ApiResponse[DeviceRead])
def delete_device(
    device_id: UUID,
    current_user: CurrentUser = Depends(require_permissions("device:delete")),
    db: Session = Depends(get_db),
) -> ApiResponse[DeviceRead]:
    ensure_device_scope(db, device_id, current_user)
    return ok(labops_service.delete_device(db, device_id), message="device disabled")
