from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.core.security import get_current_user
from app.schemas.auth import CurrentUser
from app.schemas.common import ApiResponse, PageData, ok
from app.schemas.repair_report import RepairReportCreate, RepairReportRead, RepairReportStatus
from app.services.business import labops_service

router = APIRouter()


@router.get("", response_model=ApiResponse[PageData[RepairReportRead]])
def list_repair_reports(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    device_id: UUID | None = None,
    reporter_id: UUID | None = None,
    status: RepairReportStatus | None = None,
    fault_type: str | None = Query(default=None, max_length=64),
) -> ApiResponse[PageData[RepairReportRead]]:
    return ok(
        labops_service.list_repair_reports(
            page=page,
            page_size=page_size,
            device_id=device_id,
            reporter_id=reporter_id,
            status=status,
            fault_type=fault_type,
        )
    )


@router.post("", response_model=ApiResponse[RepairReportRead], status_code=201)
def create_repair_report(
    payload: RepairReportCreate,
    current_user: CurrentUser = Depends(get_current_user),
) -> ApiResponse[RepairReportRead]:
    return ok(labops_service.create_repair_report(payload, current_user.id))


@router.get("/{report_id}", response_model=ApiResponse[RepairReportRead])
def get_repair_report(report_id: UUID) -> ApiResponse[RepairReportRead]:
    return ok(labops_service.get_repair_report(report_id))
