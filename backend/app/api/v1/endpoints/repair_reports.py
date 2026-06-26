from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.schemas.auth import CurrentUser
from app.schemas.common import ApiResponse, PageData, ok, utc_now
from app.schemas.repair_report import RepairReportCreate, RepairReportRead, RepairReportStatus

router = APIRouter()

DEMO_REPAIR_REPORT_ID = UUID("30000000-0000-0000-0000-000000000001")
DEMO_DEVICE_ID = UUID("10000000-0000-0000-0000-000000000001")


def demo_repair_report(report_id: UUID = DEMO_REPAIR_REPORT_ID) -> RepairReportRead:
    now = utc_now()
    return RepairReportRead(
        id=report_id,
        device_id=DEMO_DEVICE_ID,
        reporter_id=UUID("00000000-0000-0000-0000-000000000001"),
        fault_type="hardware",
        description="设备启动后异常震动",
        status=RepairReportStatus.submitted,
        created_at=now,
        updated_at=now,
    )


@router.get("", response_model=ApiResponse[PageData[RepairReportRead]])
def list_repair_reports(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    device_id: UUID | None = None,
    reporter_id: UUID | None = None,
    status: RepairReportStatus | None = None,
    fault_type: str | None = None,
    db: Session = Depends(get_db),
) -> ApiResponse[PageData[RepairReportRead]]:
    _ = (device_id, reporter_id, status, fault_type, db)
    return ok(PageData(items=[demo_repair_report()], page=page, page_size=page_size, total=1))


@router.post("", response_model=ApiResponse[RepairReportRead], status_code=201)
def create_repair_report(
    payload: RepairReportCreate,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ApiResponse[RepairReportRead]:
    _ = db
    now = utc_now()
    return ok(
        RepairReportRead(
            id=DEMO_REPAIR_REPORT_ID,
            reporter_id=current_user.id,
            status=RepairReportStatus.submitted,
            created_at=now,
            updated_at=now,
            **payload.model_dump(),
        )
    )


@router.get("/{report_id}", response_model=ApiResponse[RepairReportRead])
def get_repair_report(report_id: UUID, db: Session = Depends(get_db)) -> ApiResponse[RepairReportRead]:
    _ = db
    return ok(demo_repair_report(report_id))
