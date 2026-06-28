from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import require_permissions
from app.db.session import get_db
from app.schemas.analytics import OperationReportRead
from app.schemas.auth import CurrentUser
from app.schemas.common import ApiResponse, ok
from app.services.business import labops_service

router = APIRouter()


def is_device_owner(current_user: CurrentUser) -> bool:
    roles = set(current_user.roles)
    return "device_owner" in roles and not roles.intersection({"lab_admin", "system_admin"})


def is_self_service_user(current_user: CurrentUser) -> bool:
    roles = set(current_user.roles)
    return bool(roles.intersection({"ordinary_user", "student"})) and not roles.intersection({"lab_admin", "system_admin", "teacher", "device_owner"})


@router.get("/operation-report", response_model=ApiResponse[OperationReportRead])
def get_operation_report(
    start_date: date | None = None,
    end_date: date | None = None,
    current_user: CurrentUser = Depends(require_permissions("analytics:view")),
    db: Session = Depends(get_db),
) -> ApiResponse[OperationReportRead]:
    return ok(
        labops_service.operation_report(
            db,
            start_date,
            end_date,
            applicant_id=current_user.id if is_self_service_user(current_user) else None,
            reporter_id=current_user.id if is_self_service_user(current_user) else None,
            device_manager_id=current_user.id if is_device_owner(current_user) else None,
        )
    )
