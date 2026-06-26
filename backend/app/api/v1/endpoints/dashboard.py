from datetime import date, timedelta
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.common import ApiResponse, ok
from app.schemas.dashboard import DashboardSummary, StatusCount, TrendPoint

router = APIRouter()


@router.get("/summary", response_model=ApiResponse[DashboardSummary])
def get_summary(db: Session = Depends(get_db)) -> ApiResponse[DashboardSummary]:
    _ = db
    return ok(
        DashboardSummary(
            device_total=128,
            device_available=96,
            today_reservations=18,
            pending_repairs=7,
            open_work_orders=5,
        )
    )


@router.get("/device-utilization", response_model=ApiResponse[list[TrendPoint]])
def get_device_utilization(
    start_date: date | None = None,
    end_date: date | None = None,
    lab_id: UUID | None = None,
    db: Session = Depends(get_db),
) -> ApiResponse[list[TrendPoint]]:
    _ = (end_date, lab_id, db)
    base = start_date or date.today() - timedelta(days=6)
    return ok([TrendPoint(date=base + timedelta(days=index), value=62 + index * 3) for index in range(7)])


@router.get("/reservation-status", response_model=ApiResponse[list[StatusCount]])
def get_reservation_status(db: Session = Depends(get_db)) -> ApiResponse[list[StatusCount]]:
    _ = db
    return ok(
        [
            StatusCount(status="pending", count=6),
            StatusCount(status="approved", count=24),
            StatusCount(status="rejected", count=3),
            StatusCount(status="canceled", count=2),
        ]
    )


@router.get("/repair-trend", response_model=ApiResponse[list[TrendPoint]])
def get_repair_trend(
    start_date: date | None = None,
    end_date: date | None = None,
    lab_id: UUID | None = None,
    db: Session = Depends(get_db),
) -> ApiResponse[list[TrendPoint]]:
    _ = (end_date, lab_id, db)
    base = start_date or date.today() - timedelta(days=6)
    return ok([TrendPoint(date=base + timedelta(days=index), value=(index % 3) + 1) for index in range(7)])
