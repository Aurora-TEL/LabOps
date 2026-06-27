from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import require_any_permission, require_permissions
from app.db.session import get_db
from app.models import Device, RepairReport
from app.schemas.auth import CurrentUser
from app.schemas.common import ApiResponse, PageData, ok
from app.schemas.repair_report import RepairReportCreate, RepairReportRead, RepairReportStatus
from app.services.business import labops_service

router = APIRouter()


def is_device_owner(current_user: CurrentUser) -> bool:
    roles = set(current_user.roles)
    return "device_owner" in roles and not roles.intersection({"lab_admin", "system_admin"})


def can_view_all(current_user: CurrentUser) -> bool:
    return "repair:view_all" in current_user.permissions


def ensure_can_view_report(db: Session, report_id: UUID, current_user: CurrentUser, report: RepairReportRead | None = None) -> None:
    if not can_view_all(current_user):
        if report is not None and report.reporter_id == current_user.id:
            return
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="repair report is outside current user")
    if is_device_owner(current_user):
        statement = (
            select(RepairReport.id)
            .join(Device, RepairReport.device_id == Device.id)
            .where(RepairReport.id == report_id, Device.manager_id == current_user.id)
        )
        if db.scalar(statement) is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="repair report is outside owned devices")


@router.get("", response_model=ApiResponse[PageData[RepairReportRead]])
def list_repair_reports(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    device_id: UUID | None = None,
    reporter_id: UUID | None = None,
    status: RepairReportStatus | None = None,
    fault_type: str | None = Query(default=None, max_length=64),
    current_user: CurrentUser = Depends(require_any_permission("repair:view_self", "repair:view_all")),
    db: Session = Depends(get_db),
) -> ApiResponse[PageData[RepairReportRead]]:
    reporter_filter = reporter_id if can_view_all(current_user) else current_user.id
    manager_filter = current_user.id if is_device_owner(current_user) else None
    return ok(
        labops_service.list_repair_reports(
            db,
            page=page,
            page_size=page_size,
            device_id=device_id,
            reporter_id=reporter_filter,
            status=status,
            fault_type=fault_type,
            device_manager_id=manager_filter,
        )
    )


@router.post("", response_model=ApiResponse[RepairReportRead], status_code=201)
def create_repair_report(
    payload: RepairReportCreate,
    current_user: CurrentUser = Depends(require_permissions("repair:create")),
    db: Session = Depends(get_db),
) -> ApiResponse[RepairReportRead]:
    return ok(labops_service.create_repair_report(db, payload, current_user.id))


@router.get("/{report_id}", response_model=ApiResponse[RepairReportRead])
def get_repair_report(
    report_id: UUID,
    current_user: CurrentUser = Depends(require_any_permission("repair:view_self", "repair:view_all")),
    db: Session = Depends(get_db),
) -> ApiResponse[RepairReportRead]:
    report = labops_service.get_repair_report(db, report_id)
    ensure_can_view_report(db, report_id, current_user, report)
    return ok(report)
