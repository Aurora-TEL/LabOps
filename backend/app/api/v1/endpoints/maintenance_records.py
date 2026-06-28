from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import require_any_permission, require_permissions
from app.db.session import get_db
from app.models import Device
from app.schemas.auth import CurrentUser
from app.schemas.common import ApiResponse, PageData, ok
from app.schemas.maintenance import MaintenanceRecordCreate, MaintenanceRecordRead, MaintenanceType
from app.services.maintenance import maintenance_service

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


@router.get("", response_model=ApiResponse[PageData[MaintenanceRecordRead]])
def list_maintenance_records(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    device_id: UUID | None = None,
    work_order_id: UUID | None = None,
    maintenance_type: MaintenanceType | None = None,
    current_user: CurrentUser = Depends(require_permissions("device:view")),
    db: Session = Depends(get_db),
) -> ApiResponse[PageData[MaintenanceRecordRead]]:
    if device_id is not None:
        ensure_device_scope(db, device_id, current_user)
    return ok(
        maintenance_service.list_records(
            db,
            page=page,
            page_size=page_size,
            device_id=device_id,
            work_order_id=work_order_id,
            maintenance_type=maintenance_type,
            device_manager_id=scoped_manager_id(current_user),
        )
    )


@router.post("", response_model=ApiResponse[MaintenanceRecordRead], status_code=201)
def create_maintenance_record(
    payload: MaintenanceRecordCreate,
    current_user: CurrentUser = Depends(require_any_permission("device:update", "work_order:close")),
    db: Session = Depends(get_db),
) -> ApiResponse[MaintenanceRecordRead]:
    ensure_device_scope(db, payload.device_id, current_user)
    return ok(maintenance_service.create_record(db, payload=payload, maintainer_id=current_user.id))
