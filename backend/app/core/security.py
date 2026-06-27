from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from app.core.config import settings
from app.schemas.auth import CurrentUser
from app.services.auth import ALGORITHM

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


def credentials_exception(detail: str = "invalid or missing authentication token") -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_current_user(token: Annotated[str | None, Depends(oauth2_scheme)] = None) -> CurrentUser:
    if not token:
        raise credentials_exception()
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        username = payload.get("username")
        real_name = payload.get("real_name")
        if not user_id or not username or not real_name:
            raise credentials_exception()
        return CurrentUser(
            id=UUID(str(user_id)),
            username=str(username),
            real_name=str(real_name),
            roles=list(payload.get("roles") or []),
            permissions=list(payload.get("permissions") or []),
        )
    except (JWTError, ValueError):
        raise credentials_exception() from None


def require_roles(*allowed_roles: str):
    async def dependency(current_user: Annotated[CurrentUser, Depends(get_current_user)]) -> CurrentUser:
        if not set(current_user.roles).intersection(allowed_roles):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="insufficient role")
        return current_user

    return dependency


def require_permissions(*required_permissions: str):
    async def dependency(current_user: Annotated[CurrentUser, Depends(get_current_user)]) -> CurrentUser:
        if not set(required_permissions).issubset(set(current_user.permissions)):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="insufficient permission")
        return current_user

    return dependency


def require_any_permission(*allowed_permissions: str):
    async def dependency(current_user: Annotated[CurrentUser, Depends(get_current_user)]) -> CurrentUser:
        if not set(current_user.permissions).intersection(allowed_permissions):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="insufficient permission")
        return current_user

    return dependency
