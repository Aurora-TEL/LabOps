from datetime import date
from uuid import UUID

from fastapi import APIRouter

from app.schemas.common import ApiResponse, ok
from app.schemas.dashboard import DashboardSummary, StatusCount, TrendPoint
from app.services.business import labops_service

router = APIRouter()


@router.get("/summary", response_model=ApiResponse[DashboardSummary])
def get_summary() -> ApiResponse[DashboardSummary]:
    return ok(labops_service.dashboard_summary())


@router.get("/device-utilization", response_model=ApiResponse[list[TrendPoint]])
def get_device_utilization(
    start_date: date | None = None,
    end_date: date | None = None,
    lab_id: UUID | None = None,
) -> ApiResponse[list[TrendPoint]]:
    return ok(labops_service.device_utilization(start_date, end_date, lab_id))


@router.get("/reservation-status", response_model=ApiResponse[list[StatusCount]])
def get_reservation_status() -> ApiResponse[list[StatusCount]]:
    return ok(labops_service.reservation_status())


@router.get("/repair-trend", response_model=ApiResponse[list[TrendPoint]])
def get_repair_trend(
    start_date: date | None = None,
    end_date: date | None = None,
    lab_id: UUID | None = None,
) -> ApiResponse[list[TrendPoint]]:
    return ok(labops_service.repair_trend(start_date, end_date, lab_id))
