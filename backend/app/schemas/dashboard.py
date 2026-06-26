from datetime import date

from pydantic import BaseModel


class DashboardSummary(BaseModel):
    device_total: int
    device_available: int
    today_reservations: int
    pending_repairs: int
    open_work_orders: int


class TrendPoint(BaseModel):
    date: date
    value: float


class StatusCount(BaseModel):
    status: str
    count: int
