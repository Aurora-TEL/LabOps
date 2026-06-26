from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.core.security import get_current_user
from app.schemas.auth import CurrentUser
from app.schemas.common import ApiResponse, PageData, ok
from app.schemas.reservation import ReservationCreate, ReservationRead, ReservationReject, ReservationStatus
from app.services.business import labops_service

router = APIRouter()


@router.get("", response_model=ApiResponse[PageData[ReservationRead]])
def list_reservations(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    device_id: UUID | None = None,
    applicant_id: UUID | None = None,
    status: ReservationStatus | None = None,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
) -> ApiResponse[PageData[ReservationRead]]:
    return ok(
        labops_service.list_reservations(
            page=page,
            page_size=page_size,
            device_id=device_id,
            applicant_id=applicant_id,
            status=status,
            start_time=start_time,
            end_time=end_time,
        )
    )


@router.post("", response_model=ApiResponse[ReservationRead], status_code=201)
def create_reservation(
    payload: ReservationCreate,
    current_user: CurrentUser = Depends(get_current_user),
) -> ApiResponse[ReservationRead]:
    return ok(labops_service.create_reservation(payload, current_user.id))


@router.get("/{reservation_id}", response_model=ApiResponse[ReservationRead])
def get_reservation(reservation_id: UUID) -> ApiResponse[ReservationRead]:
    return ok(labops_service.get_reservation(reservation_id))


@router.post("/{reservation_id}/approve", response_model=ApiResponse[ReservationRead])
def approve_reservation(
    reservation_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
) -> ApiResponse[ReservationRead]:
    return ok(labops_service.approve_reservation(reservation_id, current_user.id))


@router.post("/{reservation_id}/reject", response_model=ApiResponse[ReservationRead])
def reject_reservation(
    reservation_id: UUID,
    payload: ReservationReject,
    current_user: CurrentUser = Depends(get_current_user),
) -> ApiResponse[ReservationRead]:
    return ok(labops_service.reject_reservation(reservation_id, current_user.id, payload.reject_reason))


@router.post("/{reservation_id}/cancel", response_model=ApiResponse[ReservationRead])
def cancel_reservation(reservation_id: UUID) -> ApiResponse[ReservationRead]:
    return ok(labops_service.cancel_reservation(reservation_id))
