from fastapi import APIRouter, Depends

from app.core.config import settings
from app.core.security import get_current_user
from app.schemas.auth import CurrentUser, LoginRequest, TokenResponse
from app.schemas.common import ApiResponse, ok

router = APIRouter()


@router.post("/login", response_model=ApiResponse[TokenResponse])
def login(payload: LoginRequest) -> ApiResponse[TokenResponse]:
    user = CurrentUser(
        id="00000000-0000-0000-0000-000000000001",
        username=payload.username,
        real_name="演示用户",
        roles=["admin"],
    )
    token = TokenResponse(
        access_token="placeholder.jwt.token",
        expires_in=settings.access_token_expire_minutes * 60,
        user=user,
    )
    return ok(token)


@router.post("/logout", response_model=ApiResponse[dict[str, bool]])
def logout() -> ApiResponse[dict[str, bool]]:
    return ok({"revoked": False}, message="logout placeholder")


@router.get("/me", response_model=ApiResponse[CurrentUser])
async def me(current_user: CurrentUser = Depends(get_current_user)) -> ApiResponse[CurrentUser]:
    return ok(current_user)
