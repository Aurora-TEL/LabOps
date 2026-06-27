from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.common import ApiResponse, ok
from app.schemas.dashboard import DashboardSummary, StatusCount, TrendPoint
from app.services.business import labops_service

router = APIRouter()


@router.get("/summary", response_model=ApiResponse[DashboardSummary])
def get_summary(db: Session = Depends(get_db)) -> ApiResponse[DashboardSummary]:
    return ok(labops_service.dashboard_summary(db))


@router.get("/device-utilization", response_model=ApiResponse[list[TrendPoint]])
def get_device_utilization(
    start_date: date | None = None,
    end_date: date | None = None,
    lab_id: UUID | None = None,
    db: Session = Depends(get_db),
) -> ApiResponse[list[TrendPoint]]:
    return ok(labops_service.device_utilization(db, start_date, end_date, lab_id))


@router.get("/reservation-status", response_model=ApiResponse[list[StatusCount]])
def get_reservation_status(db: Session = Depends(get_db)) -> ApiResponse[list[StatusCount]]:
    return ok(labops_service.reservation_status(db))


@router.get("/repair-trend", response_model=ApiResponse[list[TrendPoint]])
def get_repair_trend(
    start_date: date | None = None,
    end_date: date | None = None,
    lab_id: UUID | None = None,
    db: Session = Depends(get_db),
) -> ApiResponse[list[TrendPoint]]:
    return ok(labops_service.repair_trend(db, start_date, end_date, lab_id))
