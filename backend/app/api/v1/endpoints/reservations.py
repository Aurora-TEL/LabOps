from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import get_current_user, require_any_permission, require_permissions
from app.db.session import get_db
from app.models import Device, Reservation
from app.schemas.auth import CurrentUser
from app.schemas.common import ApiResponse, PageData, ok
from app.schemas.reservation import ReservationCreate, ReservationRead, ReservationReject, ReservationStatus
from app.services.business import labops_service

router = APIRouter()


def is_device_owner(current_user: CurrentUser) -> bool:
    roles = set(current_user.roles)
    return "device_owner" in roles and not roles.intersection({"lab_admin", "system_admin"})


def can_view_all(current_user: CurrentUser) -> bool:
    return "reservation:view_all" in current_user.permissions


def ensure_can_manage_reservation(db: Session, reservation_id: UUID, current_user: CurrentUser) -> None:
    if not is_device_owner(current_user):
        return
    statement = (
        select(Reservation.id)
        .join(Device, Reservation.device_id == Device.id)
        .where(Reservation.id == reservation_id, Device.manager_id == current_user.id)
    )
    if db.scalar(statement) is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="reservation is outside owned devices")


@router.get("", response_model=ApiResponse[PageData[ReservationRead]])
def list_reservations(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    device_id: UUID | None = None,
    applicant_id: UUID | None = None,
    status: ReservationStatus | None = None,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
    current_user: CurrentUser = Depends(require_any_permission("reservation:view_self", "reservation:view_all")),
    db: Session = Depends(get_db),
) -> ApiResponse[PageData[ReservationRead]]:
    applicant_filter = applicant_id if can_view_all(current_user) else current_user.id
    manager_filter = current_user.id if is_device_owner(current_user) else None
    return ok(
        labops_service.list_reservations(
            db,
            page=page,
            page_size=page_size,
            device_id=device_id,
            applicant_id=applicant_filter,
            status=status,
            start_time=start_time,
            end_time=end_time,
            device_manager_id=manager_filter,
        )
    )


@router.post("", response_model=ApiResponse[ReservationRead], status_code=201)
def create_reservation(
    payload: ReservationCreate,
    current_user: CurrentUser = Depends(require_permissions("reservation:create")),
    db: Session = Depends(get_db),
) -> ApiResponse[ReservationRead]:
    return ok(labops_service.create_reservation(db, payload, current_user.id))


@router.get("/{reservation_id}", response_model=ApiResponse[ReservationRead])
def get_reservation(
    reservation_id: UUID,
    current_user: CurrentUser = Depends(require_any_permission("reservation:view_self", "reservation:view_all")),
    db: Session = Depends(get_db),
) -> ApiResponse[ReservationRead]:
    reservation = labops_service.get_reservation(db, reservation_id)
    if not can_view_all(current_user) and reservation.applicant_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="reservation is outside current user")
    ensure_can_manage_reservation(db, reservation_id, current_user)
    return ok(reservation)


@router.post("/{reservation_id}/approve", response_model=ApiResponse[ReservationRead])
def approve_reservation(
    reservation_id: UUID,
    current_user: CurrentUser = Depends(require_permissions("reservation:approve")),
    db: Session = Depends(get_db),
) -> ApiResponse[ReservationRead]:
    ensure_can_manage_reservation(db, reservation_id, current_user)
    return ok(labops_service.approve_reservation(db, reservation_id, current_user.id))


@router.post("/{reservation_id}/reject", response_model=ApiResponse[ReservationRead])
def reject_reservation(
    reservation_id: UUID,
    payload: ReservationReject,
    current_user: CurrentUser = Depends(require_permissions("reservation:approve")),
    db: Session = Depends(get_db),
) -> ApiResponse[ReservationRead]:
    ensure_can_manage_reservation(db, reservation_id, current_user)
    return ok(labops_service.reject_reservation(db, reservation_id, current_user.id, payload.reject_reason))


@router.post("/{reservation_id}/cancel", response_model=ApiResponse[ReservationRead])
def cancel_reservation(
    reservation_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ApiResponse[ReservationRead]:
    reservation = labops_service.get_reservation(db, reservation_id)
    can_cancel_all = "reservation:cancel_all" in current_user.permissions
    can_cancel_self = "reservation:cancel_self" in current_user.permissions and reservation.applicant_id == current_user.id
    if not can_cancel_all and not can_cancel_self:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="insufficient permission")
    ensure_can_manage_reservation(db, reservation_id, current_user)
    return ok(labops_service.cancel_reservation(db, reservation_id))
