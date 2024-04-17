from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, ConfigDict, constr

from core.config import settings
from schemas.mixins import CreatedMixinSchema, IdMixinSchema
from schemas.role_schema import RoleInDWithExpireAt, UserRoleSelfRequest


class UserID(IdMixinSchema):
    pass


class UserName(BaseModel):
    """Модель пользователя с полем username для logout"""

    username: str


class Email(BaseModel):
    email: EmailStr


class BaseUser(UserName, Email):
    """Базовая модель пользователя."""

    first_name: str | None = None
    last_name: str | None = None

    model_config = ConfigDict(from_attributes=True)


class BaseUserSocialNetwork(BaseUser):
    """Базовая модель пользователя для регистрации через соц. сети."""

    social_id: str
    social_name: str


class UserSelfResponse(BaseUser):
    """Mодель ответа эндпоинта me пользователя."""

    modified_at: datetime
    roles: list[UserRoleSelfRequest]


class UserCreate(BaseUser):
    """Модель для создания пользователя."""

    password: constr(  # type: ignore[valid-type]
        min_length=settings.min_password_input_length,
        max_length=settings.max_password_input_length,
    )


class UserCreateInDB(BaseUser):
    """Модель для cохранения нового пользователя в БД."""

    hashed_password: str


class UserInDBBase(CreatedMixinSchema, BaseUser):
    """Полнная модель пользователя с зашфрованным паролем"""

    hashed_password: str
    is_active: bool


class UserInDBFull(IdMixinSchema, UserInDBBase):
    """Полнная модель пользователя с зашфрованным паролем и ролями"""

    roles: list[RoleInDWithExpireAt]


class UserSelfUpdate(BaseModel):
    """Модель для самостоятельного изменения данных пользователя."""

    username: str | None = None
    email: EmailStr | None = None
    first_name: str | None = None
    last_name: str | None = None
    password: (  # type: ignore[valid-type]
        constr(
            min_length=settings.min_password_input_length,
            max_length=settings.max_password_input_length,
        )
        | None
    ) = None


class UserAdminUpdate(UserSelfUpdate):
    """Модель для изменения данных пользователя админом."""

    is_active: bool | None = None


class UserHistory(BaseModel):
    created_at: datetime
    user_agent: str
    activity: str

    model_config = ConfigDict(from_attributes=True)


class UserHistoryInDB(BaseModel):
    user_id: UUID
    user_agent: str
    activity: str
