from fastapi import APIRouter

from app.api.v1.endpoints import (
    audit_logs,
    analytics,
    auth,
    dashboard,
    devices,
    health,
    maintenance_records,
    notifications,
    repair_reports,
    reservations,
    system_management,
    work_orders,
)

api_router = APIRouter()
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(devices.router, prefix="/devices", tags=["devices"])
api_router.include_router(reservations.router, prefix="/reservations", tags=["reservations"])
api_router.include_router(repair_reports.router, prefix="/repair-reports", tags=["repair-reports"])
api_router.include_router(work_orders.router, prefix="/work-orders", tags=["work-orders"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
api_router.include_router(audit_logs.router, prefix="/audit-logs", tags=["audit-logs"])
api_router.include_router(system_management.router, prefix="/system", tags=["system-management"])
api_router.include_router(maintenance_records.router, prefix="/maintenance-records", tags=["maintenance-records"])
