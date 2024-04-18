from datetime import datetime
from pydantic import BaseModel
from schemas.mixins import CreatedMixinSchema, IdMixinSchema


class RoleTitle(BaseModel):
    title: str


class RoleBase(RoleTitle):
    description: str


class RoleInDB(IdMixinSchema, RoleBase):
    pass

    
class RoleInDBFull(CreatedMixinSchema, RoleInDB):
    pass


class RoleUpdate(BaseModel):
    title: str | None = None
    description: str | None = None


class UserRoleSelfRequest(RoleUpdate):
    expire_at: datetime | None


class RoleInDWithExpireAt(UserRoleSelfRequest):
    """Для показа в эндпоинтах с учетом срока действия."""

    expire_at: datetime | None
    is_active: bool
