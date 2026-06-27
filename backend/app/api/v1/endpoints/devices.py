from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.common import ApiResponse, PageData, ok
from app.schemas.device import DeviceCreate, DeviceRead, DeviceStatus, DeviceStatusUpdate, DeviceUpdate
from app.services.business import labops_service

router = APIRouter()


@router.get("", response_model=ApiResponse[PageData[DeviceRead]])
def list_devices(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    keyword: str | None = Query(default=None, max_length=128),
    lab_id: UUID | None = None,
    category_id: UUID | None = None,
    status: DeviceStatus | None = None,
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
        )
    )


@router.post("", response_model=ApiResponse[DeviceRead], status_code=201)
def create_device(payload: DeviceCreate, db: Session = Depends(get_db)) -> ApiResponse[DeviceRead]:
    return ok(labops_service.create_device(db, payload))


@router.get("/{device_id}", response_model=ApiResponse[DeviceRead])
def get_device(device_id: UUID, db: Session = Depends(get_db)) -> ApiResponse[DeviceRead]:
    return ok(labops_service.get_device(db, device_id))


@router.put("/{device_id}", response_model=ApiResponse[DeviceRead])
def update_device(device_id: UUID, payload: DeviceUpdate, db: Session = Depends(get_db)) -> ApiResponse[DeviceRead]:
    return ok(labops_service.update_device(db, device_id, payload))


@router.patch("/{device_id}/status", response_model=ApiResponse[DeviceRead])
def update_device_status(
    device_id: UUID,
    payload: DeviceStatusUpdate,
    db: Session = Depends(get_db),
) -> ApiResponse[DeviceRead]:
    _ = payload.reason
    return ok(labops_service.update_device_status(db, device_id, payload.status))


@router.delete("/{device_id}", response_model=ApiResponse[DeviceRead])
def delete_device(device_id: UUID, db: Session = Depends(get_db)) -> ApiResponse[DeviceRead]:
    return ok(labops_service.delete_device(db, device_id), message="device disabled")
