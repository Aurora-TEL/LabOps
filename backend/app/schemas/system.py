from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import TimestampMixin


class UserStatus(StrEnum):
    active = "active"
    disabled = "disabled"
    locked = "locked"


class PermissionRead(BaseModel):
    id: UUID
    code: str
    name: str
    resource: str
    action: str
    description: str | None = None


class RoleRead(TimestampMixin):
    id: UUID
    code: str
    name: str
    description: str | None = None
    is_system: bool
    permissions: list[PermissionRead] = Field(default_factory=list)
    user_count: int = 0


class ManagedUserRead(TimestampMixin):
    id: UUID
    username: str
    real_name: str
    email: str | None = None
    phone: str | None = None
    department: str | None = None
    student_no: str | None = None
    employee_no: str | None = None
    status: UserStatus
    last_login_at: datetime | None = None
    roles: list[RoleRead] = Field(default_factory=list)


class UserStatusUpdate(BaseModel):
    status: UserStatus


class UserRoleUpdate(BaseModel):
    role_codes: list[str] = Field(min_length=1, max_length=10)


class SystemManagementSummary(BaseModel):
    user_total: int
    active_users: int
    disabled_users: int
    role_total: int
    permission_total: int
