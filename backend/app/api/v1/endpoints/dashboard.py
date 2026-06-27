from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import require_permissions
from app.db.session import get_db
from app.schemas.auth import CurrentUser
from app.schemas.common import ApiResponse, ok
from app.schemas.dashboard import DashboardSummary, StatusCount, TrendPoint
from app.services.business import labops_service

router = APIRouter()


def is_device_owner(current_user: CurrentUser) -> bool:
    roles = set(current_user.roles)
    return "device_owner" in roles and not roles.intersection({"lab_admin", "system_admin"})


def is_self_service_user(current_user: CurrentUser) -> bool:
    roles = set(current_user.roles)
    return bool(roles.intersection({"ordinary_user", "student"})) and not roles.intersection({"lab_admin", "system_admin", "teacher", "device_owner"})


@router.get("/summary", response_model=ApiResponse[DashboardSummary])
def get_summary(
    current_user: CurrentUser = Depends(require_permissions("dashboard:view")),
    db: Session = Depends(get_db),
) -> ApiResponse[DashboardSummary]:
    return ok(
        labops_service.dashboard_summary(
            db,
            applicant_id=current_user.id if is_self_service_user(current_user) else None,
            reporter_id=current_user.id if is_self_service_user(current_user) else None,
            device_manager_id=current_user.id if is_device_owner(current_user) else None,
        )
    )


@router.get("/device-utilization", response_model=ApiResponse[list[TrendPoint]])
def get_device_utilization(
    start_date: date | None = None,
    end_date: date | None = None,
    lab_id: UUID | None = None,
    current_user: CurrentUser = Depends(require_permissions("dashboard:view")),
    db: Session = Depends(get_db),
) -> ApiResponse[list[TrendPoint]]:
    return ok(
        labops_service.device_utilization(
            db,
            start_date,
            end_date,
            lab_id,
            device_manager_id=current_user.id if is_device_owner(current_user) else None,
        )
    )


@router.get("/reservation-status", response_model=ApiResponse[list[StatusCount]])
def get_reservation_status(
    current_user: CurrentUser = Depends(require_permissions("dashboard:view")),
    db: Session = Depends(get_db),
) -> ApiResponse[list[StatusCount]]:
    return ok(
        labops_service.reservation_status(
            db,
            applicant_id=current_user.id if is_self_service_user(current_user) else None,
            device_manager_id=current_user.id if is_device_owner(current_user) else None,
        )
    )


@router.get("/repair-trend", response_model=ApiResponse[list[TrendPoint]])
def get_repair_trend(
    start_date: date | None = None,
    end_date: date | None = None,
    lab_id: UUID | None = None,
    current_user: CurrentUser = Depends(require_permissions("dashboard:view")),
    db: Session = Depends(get_db),
) -> ApiResponse[list[TrendPoint]]:
    return ok(
        labops_service.repair_trend(
            db,
            start_date,
            end_date,
            lab_id,
            reporter_id=current_user.id if is_self_service_user(current_user) else None,
            device_manager_id=current_user.id if is_device_owner(current_user) else None,
        )
    )
