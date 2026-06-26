from typing import Annotated
from uuid import UUID

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from app.schemas.auth import CurrentUser

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


async def get_current_user(token: Annotated[str | None, Depends(oauth2_scheme)] = None) -> CurrentUser:
    """Authentication placeholder.

    Real JWT decoding, token revocation, and permission checks will be added when
    the user/role tables are implemented.
    """
    return CurrentUser(
        id=UUID("00000000-0000-0000-0000-000000000001"),
        username="demo",
        real_name="演示用户",
        roles=["admin"],
    )
