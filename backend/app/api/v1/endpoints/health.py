from fastapi import APIRouter, Depends, Response
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.common import ApiResponse, ok

router = APIRouter()


class HealthStatus(BaseModel):
    status: str
    database: str | None = None


@router.get("/live", response_model=ApiResponse[HealthStatus])
def live() -> ApiResponse[HealthStatus]:
    return ok(HealthStatus(status="ok"))


@router.get("/ready", response_model=ApiResponse[HealthStatus])
def ready(response: Response, db: Session = Depends(get_db)) -> ApiResponse[HealthStatus]:
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        response.status_code = 503
        return ok(HealthStatus(status="degraded", database="unavailable"), message="database unavailable")

    return ok(HealthStatus(status="ok", database="ok"))
