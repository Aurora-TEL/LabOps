from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user, require_permissions
from app.db.session import get_db
from app.schemas.auth import CurrentUser, LoginRequest, TokenResponse
from app.schemas.common import ApiResponse, ok
from app.services.auth import DisabledUserError, InvalidCredentialsError, authenticate_user, issue_token

router = APIRouter()


@router.post("/login", response_model=ApiResponse[TokenResponse])
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> ApiResponse[TokenResponse]:
    try:
        user = authenticate_user(db, payload.username, payload.password)
    except InvalidCredentialsError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid username or password") from None
    except DisabledUserError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="user is disabled") from None
    return ok(issue_token(user))


@router.post("/logout", response_model=ApiResponse[dict[str, bool]])
def logout() -> ApiResponse[dict[str, bool]]:
    return ok({"revoked": False}, message="logout placeholder")


@router.get("/me", response_model=ApiResponse[CurrentUser])
async def me(current_user: CurrentUser = Depends(get_current_user)) -> ApiResponse[CurrentUser]:
    return ok(current_user)


@router.get("/rbac-demo", response_model=ApiResponse[CurrentUser])
async def rbac_demo(
    current_user: Annotated[CurrentUser, Depends(require_permissions("role:manage"))],
) -> ApiResponse[CurrentUser]:
    return ok(current_user)
