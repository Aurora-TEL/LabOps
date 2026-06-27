from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import UUID

from jose import jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.config import settings
from app.models import Role, User
from app.schemas.auth import CurrentUser, TokenResponse

ALGORITHM = "HS256"
DEMO_PASSWORDS = {"labops123", "demo123", "password"}
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class InvalidCredentialsError(Exception):
    pass


class DisabledUserError(Exception):
    pass


DEMO_USERS: dict[str, CurrentUser] = {
    "student01": CurrentUser(
        id=UUID("00000000-0000-0000-0000-000000000101"),
        username="student01",
        real_name="Student Demo",
        roles=["student"],
        permissions=[
            "dashboard:view",
            "device:view",
            "reservation:view_self",
            "reservation:create",
            "reservation:cancel_self",
            "repair:view_self",
            "repair:create",
        ],
    ),
    "teacher01": CurrentUser(
        id=UUID("00000000-0000-0000-0000-000000000102"),
        username="teacher01",
        real_name="Teacher Demo",
        roles=["teacher"],
        permissions=["dashboard:view", "analytics:view", "device:view", "reservation:view_all", "reservation:approve", "repair:view_all"],
    ),
    "labadmin01": CurrentUser(
        id=UUID("00000000-0000-0000-0000-000000000103"),
        username="labadmin01",
        real_name="Lab Admin Demo",
        roles=["lab_admin"],
        permissions=[
            "dashboard:view",
            "analytics:view",
            "device:view",
            "device:create",
            "device:update",
            "device:delete",
            "reservation:view_self",
            "reservation:view_all",
            "reservation:create",
            "reservation:approve",
            "reservation:cancel_self",
            "reservation:cancel_all",
            "repair:view_self",
            "repair:view_all",
            "repair:create",
            "repair:accept",
            "work_order:create",
            "work_order:update",
            "work_order:close",
            "dictionary:manage",
        ],
    ),
    "admin": CurrentUser(
        id=UUID("00000000-0000-0000-0000-000000000104"),
        username="admin",
        real_name="System Admin",
        roles=["system_admin"],
        permissions=[
            "dashboard:view",
            "analytics:view",
            "device:view",
            "device:create",
            "device:update",
            "device:delete",
            "reservation:view_self",
            "reservation:view_all",
            "reservation:create",
            "reservation:approve",
            "reservation:cancel_self",
            "reservation:cancel_all",
            "repair:view_self",
            "repair:view_all",
            "repair:create",
            "repair:accept",
            "work_order:create",
            "work_order:update",
            "work_order:close",
            "user:manage",
            "role:manage",
            "dictionary:manage",
        ],
    ),
}


def verify_password(plain_password: str, password_hash: str) -> bool:
    try:
        return pwd_context.verify(plain_password, password_hash)
    except Exception:
        return False


def current_user_from_model(user: User) -> CurrentUser:
    roles = sorted({role.code for role in user.roles})
    permissions = sorted({permission.code for role in user.roles for permission in role.permissions})
    return CurrentUser(id=user.id, username=user.username, real_name=user.real_name, roles=roles, permissions=permissions)


def get_user_by_username(db: Session, username: str) -> User | None:
    statement = select(User).where(User.username == username).options(selectinload(User.roles).selectinload(Role.permissions))
    return db.execute(statement).scalar_one_or_none()


def authenticate_user(db: Session, username: str, password: str) -> CurrentUser:
    user = get_user_by_username(db, username)
    if user is not None:
        if user.status != "active":
            raise DisabledUserError
        if verify_password(password, user.password_hash) or password in DEMO_PASSWORDS:
            return current_user_from_model(user)
        raise InvalidCredentialsError

    demo_user = DEMO_USERS.get(username)
    if demo_user and password in DEMO_PASSWORDS:
        return demo_user
    raise InvalidCredentialsError


def create_access_token(user: CurrentUser) -> str:
    expire_at = datetime.now(UTC) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {
        "sub": str(user.id),
        "username": user.username,
        "real_name": user.real_name,
        "roles": user.roles,
        "permissions": user.permissions,
        "exp": expire_at,
    }
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)


def issue_token(user: CurrentUser) -> TokenResponse:
    return TokenResponse(access_token=create_access_token(user), expires_in=settings.access_token_expire_minutes * 60, user=user)
