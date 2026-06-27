from fastapi import APIRouter

from app.api.v1.endpoints import audit_logs, auth, dashboard, devices, health, notifications, repair_reports, reservations, work_orders

api_router = APIRouter()
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(devices.router, prefix="/devices", tags=["devices"])
api_router.include_router(reservations.router, prefix="/reservations", tags=["reservations"])
api_router.include_router(repair_reports.router, prefix="/repair-reports", tags=["repair-reports"])
api_router.include_router(work_orders.router, prefix="/work-orders", tags=["work-orders"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
api_router.include_router(audit_logs.router, prefix="/audit-logs", tags=["audit-logs"])
