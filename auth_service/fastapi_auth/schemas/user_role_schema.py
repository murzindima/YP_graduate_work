from datetime import datetime
from uuid import UUID
from pydantic import BaseModel
from schemas.mixins import IdMixinSchema, CreatedMixinSchema


class UserRoleID(BaseModel):
    role_id: UUID


class UserRoleSchema(UserRoleID):
    user_id: UUID
    expire_at: datetime | None
    is_active: bool


class UserRoleInDBSchema(IdMixinSchema, CreatedMixinSchema, UserRoleSchema):
    pass


class UserRoleChange(BaseModel):
    expire_at: datetime | None = None
    is_active: bool | None = None


class UserRoleAssign(UserRoleChange):
    title: str
