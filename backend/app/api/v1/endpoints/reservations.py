from datetime import timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.schemas.auth import CurrentUser
from app.schemas.common import ApiResponse, PageData, ok, utc_now
from app.schemas.reservation import ReservationCreate, ReservationRead, ReservationReject, ReservationStatus

router = APIRouter()

DEMO_RESERVATION_ID = UUID("20000000-0000-0000-0000-000000000001")
DEMO_DEVICE_ID = UUID("10000000-0000-0000-0000-000000000001")


def demo_reservation(reservation_id: UUID = DEMO_RESERVATION_ID) -> ReservationRead:
    now = utc_now()
    return ReservationRead(
        id=reservation_id,
        device_id=DEMO_DEVICE_ID,
        applicant_id=UUID("00000000-0000-0000-0000-000000000001"),
        approver_id=None,
        start_time=now + timedelta(days=1),
        end_time=now + timedelta(days=1, hours=2),
        purpose="材料样品检测",
        status=ReservationStatus.pending,
        reject_reason=None,
        created_at=now,
        updated_at=now,
    )


@router.get("", response_model=ApiResponse[PageData[ReservationRead]])
def list_reservations(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    device_id: UUID | None = None,
    applicant_id: UUID | None = None,
    status: ReservationStatus | None = None,
    db: Session = Depends(get_db),
) -> ApiResponse[PageData[ReservationRead]]:
    _ = (device_id, applicant_id, status, db)
    return ok(PageData(items=[demo_reservation()], page=page, page_size=page_size, total=1))


@router.post("", response_model=ApiResponse[ReservationRead], status_code=201)
def create_reservation(
    payload: ReservationCreate,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ApiResponse[ReservationRead]:
    _ = db
    now = utc_now()
    return ok(
        ReservationRead(
            id=DEMO_RESERVATION_ID,
            applicant_id=current_user.id,
            approver_id=None,
            status=ReservationStatus.pending,
            reject_reason=None,
            created_at=now,
            updated_at=now,
            **payload.model_dump(),
        )
    )


@router.get("/{reservation_id}", response_model=ApiResponse[ReservationRead])
def get_reservation(reservation_id: UUID, db: Session = Depends(get_db)) -> ApiResponse[ReservationRead]:
    _ = db
    return ok(demo_reservation(reservation_id))


@router.post("/{reservation_id}/approve", response_model=ApiResponse[ReservationRead])
def approve_reservation(
    reservation_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ApiResponse[ReservationRead]:
    _ = db
    return ok(
        demo_reservation(reservation_id).model_copy(
            update={"status": ReservationStatus.approved, "approver_id": current_user.id, "updated_at": utc_now()}
        )
    )


@router.post("/{reservation_id}/reject", response_model=ApiResponse[ReservationRead])
def reject_reservation(
    reservation_id: UUID,
    payload: ReservationReject,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ApiResponse[ReservationRead]:
    _ = db
    return ok(
        demo_reservation(reservation_id).model_copy(
            update={
                "status": ReservationStatus.rejected,
                "approver_id": current_user.id,
                "reject_reason": payload.reject_reason,
                "updated_at": utc_now(),
            }
        )
    )


@router.post("/{reservation_id}/cancel", response_model=ApiResponse[ReservationRead])
def cancel_reservation(reservation_id: UUID, db: Session = Depends(get_db)) -> ApiResponse[ReservationRead]:
    _ = db
    return ok(demo_reservation(reservation_id).model_copy(update={"status": ReservationStatus.canceled, "updated_at": utc_now()}))
