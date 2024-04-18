from datetime import datetime
from uuid import UUID

from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

from core.config import settings


class Tokens(BaseModel):
    access_token: str
    refresh_token: str
    tokens_type: str


class RefreshTokenInDB(BaseModel):
    user_id: UUID
    token: str
    expire_at: datetime
    is_active: bool | None = True


class ActiveStatus(BaseModel):
    is_active: bool


class RefreshToken(BaseModel):
    token: str


oauth2_scheme = OAuth2PasswordBearer(tokenUrl=settings.prefix + "/auth/login")
