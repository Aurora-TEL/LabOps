from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.common import ApiResponse, PageData, ok, utc_now
from app.schemas.device import DeviceCreate, DeviceRead, DeviceStatus, DeviceStatusUpdate, DeviceUpdate

router = APIRouter()

DEMO_DEVICE_ID = UUID("10000000-0000-0000-0000-000000000001")


def demo_device(device_id: UUID = DEMO_DEVICE_ID) -> DeviceRead:
    now = utc_now()
    return DeviceRead(
        id=device_id,
        code="DEV-001",
        name="高速离心机",
        category_id=None,
        lab_id=None,
        manager_id=None,
        status=DeviceStatus.available,
        health_score=96.5,
        purchase_date=date(2025, 9, 1),
        created_at=now,
        updated_at=now,
    )


@router.get("", response_model=ApiResponse[PageData[DeviceRead]])
def list_devices(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    keyword: str | None = None,
    lab_id: UUID | None = None,
    category_id: UUID | None = None,
    status: DeviceStatus | None = None,
    db: Session = Depends(get_db),
) -> ApiResponse[PageData[DeviceRead]]:
    _ = (keyword, lab_id, category_id, status, db)
    return ok(PageData(items=[demo_device()], page=page, page_size=page_size, total=1))


@router.post("", response_model=ApiResponse[DeviceRead], status_code=201)
def create_device(payload: DeviceCreate, db: Session = Depends(get_db)) -> ApiResponse[DeviceRead]:
    _ = db
    now = utc_now()
    return ok(DeviceRead(id=DEMO_DEVICE_ID, created_at=now, updated_at=now, **payload.model_dump()))


@router.get("/{device_id}", response_model=ApiResponse[DeviceRead])
def get_device(device_id: UUID, db: Session = Depends(get_db)) -> ApiResponse[DeviceRead]:
    _ = db
    return ok(demo_device(device_id))


@router.put("/{device_id}", response_model=ApiResponse[DeviceRead])
def update_device(device_id: UUID, payload: DeviceUpdate, db: Session = Depends(get_db)) -> ApiResponse[DeviceRead]:
    _ = db
    current = demo_device(device_id)
    updated = current.model_copy(update=payload.model_dump(exclude_unset=True) | {"updated_at": utc_now()})
    return ok(updated)


@router.patch("/{device_id}/status", response_model=ApiResponse[DeviceRead])
def update_device_status(
    device_id: UUID,
    payload: DeviceStatusUpdate,
    db: Session = Depends(get_db),
) -> ApiResponse[DeviceRead]:
    _ = (payload.reason, db)
    return ok(demo_device(device_id).model_copy(update={"status": payload.status, "updated_at": utc_now()}))


@router.delete("/{device_id}", response_model=ApiResponse[dict[str, UUID]])
def delete_device(device_id: UUID, db: Session = Depends(get_db)) -> ApiResponse[dict[str, UUID]]:
    _ = db
    return ok({"id": device_id}, message="device delete placeholder")
