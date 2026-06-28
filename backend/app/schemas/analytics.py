from datetime import date

from pydantic import BaseModel

from app.schemas.dashboard import StatusCount, TrendPoint


class AnalyticsKpi(BaseModel):
    label: str
    value: float
    unit: str = ""
    delta: str = ""
    status: str = "normal"


class CategoryCount(BaseModel):
    name: str
    count: int


class DeviceHealthRankItem(BaseModel):
    device_id: str
    device_name: str
    status: str
    health_score: float


class OperationReportRead(BaseModel):
    start_date: date
    end_date: date
    kpis: list[AnalyticsKpi]
    reservation_trend: list[TrendPoint]
    repair_trend: list[TrendPoint]
    reservation_status: list[StatusCount]
    fault_types: list[CategoryCount]
    maintenance_types: list[CategoryCount]
    device_health: list[DeviceHealthRankItem]
