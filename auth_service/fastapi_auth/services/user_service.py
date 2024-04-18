import re
from datetime import datetime
from functools import lru_cache
from typing import Type
from uuid import UUID

import base64
import httpx
from authlib.integrations.starlette_client import OAuthError
from json import JSONDecodeError
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from core.config import settings, SocialNetworks
from core.exceptions import (
    UserNotFoundException,
    EmailAlreadyUsedException,
    UsernameAlreadyExistException,
    PasswordComplexityException,
    UsernameNotMeException,
    NotAllowedUsernameException,
    USserAlreadyBoundedToSocialNetworkException,
    UserHaveNotBoundedException,
)
from models.common import (
    User,
    UserActivityHistory,
    UserRoleModel,
    SocialAccount,
)
from schemas.social_account import SocialAccountInDB, SocialAccountUserId
from schemas.role_schema import RoleInDWithExpireAt
from schemas.user_schema import (
    UserCreate,
    UserInDBBase,
    UserInDBFull,
    UserAdminUpdate,
    UserCreateInDB,
    BaseUser,
    UserHistoryInDB,
    UserHistory,
    UserName,
    Email,
    BaseUserSocialNetwork,
)
from services.db_service import DBService, SQLAlchemyDBService

from services.utils import create_hash, PageParams


class UserDBService(SQLAlchemyDBService):
    model = User


class UserHistoryDBService(SQLAlchemyDBService):
    model = UserActivityHistory


class UserSocialAccountDBService(SQLAlchemyDBService):
    model = SocialAccount


class UserService:
    def __init__(self, db_service: Type[DBService]):
        self.db_service = db_service()
        self.user_history_service = get_user_history_service()
        self.user_social_account_service = get_user_social_account_service()

    async def create_user_in_db(
        self, db: AsyncSession, user: UserCreate
    ) -> UserInDBFull:
        """Создаем пользователя в базе данных."""
        try:
            self._check_password_complexity(user.password)
            hashed_password = create_hash(user.password)
            self._validate_username(user.username)
            user_in_db = UserCreateInDB(
                **user.model_dump(), hashed_password=hashed_password
            )
            new_user = await self.db_service.create(db=db, obj_in=user_in_db)
            return new_user
        except IntegrityError as exc:
            self._handle_integrity_error(exc, user)

    async def get_user_or_404(
        self,
        db: AsyncSession,
        username: str,
        is_admin_request: bool = False,
    ) -> UserInDBFull:
        """Получаем пользователя с ролями."""
        stmt = (
            select(User)
            .where(or_(User.username == username, User.email == username))
            .options(joinedload(User.roles).joinedload(UserRoleModel.role))
        )
        result = await self.db_service.execute(db=db, stmt=stmt)
        user = result.unique().scalars().first()
        if not user:
            raise UserNotFoundException
        user = self._create_user_in_db_full_compact_roles(
            user=user, is_admin_request=is_admin_request
        )
        return user

    async def get_or_create_user_by_social_network_data(
        self, db: AsyncSession, reg_data: BaseUserSocialNetwork
    ) -> UserInDBFull:
        """Получаем или регистрируем пользователя."""
        # ищем пользователя по имени
        by_username = await self.db_service.get(
            db=db, obj=UserName(username=reg_data.username)
        )
        if by_username:
            user = await self._check_social_account_bounded(
                db=db, user=by_username, reg_data=reg_data
            )
            if not user:
                raise UsernameAlreadyExistException(username=reg_data.username)
            # привязываем пользователя к соцсети.
            await self.user_social_account_service.create_user_social_account_in_db(
                db=db, user=user, reg_data=reg_data
            )
            return user
        # ищем пользователя по email
        by_email = await self.db_service.get(
            db=db, obj=Email(email=reg_data.email)
        )
        if by_email:
            user = await self._check_social_account_bounded(
                db=db, user=by_email, reg_data=reg_data
            )
            if not user:
                raise EmailAlreadyUsedException(email=reg_data.email)
            # привязываем пользователя к соцсети.
            await self.user_social_account_service.create_user_social_account_in_db(
                db=db, user=user, reg_data=reg_data
            )
            return user
        # если имя и почта не заняты создаем нового пользователя
        new_user_data = UserCreate(
            email=reg_data.email,
            username=reg_data.username,
            first_name=reg_data.first_name,
            last_name=reg_data.last_name,
            password=reg_data.email,
        )
        new_user = await self.create_user_in_db(db=db, user=new_user_data)
        # привязываем пользователя к соцсети.
        await (
            self.user_social_account_service.create_user_social_account_in_db(
                db=db, user=new_user, reg_data=reg_data
            )
        )
        return new_user

    async def get_users_list(
        self, db: AsyncSession, page_number: int, page_size: int
    ) -> list[UserInDBBase]:
        """Получаем список пользователей с пагинацией."""

        user_list = await self.db_service.get_list(
            db=db, offset=(page_number - 1) * page_size, limit=page_size
        )
        return user_list

    async def update_user_in_db(
        self,
        db: AsyncSession,
        new_user_data: UserAdminUpdate,
        username: str,
    ) -> UserInDBFull:
        """Изменение данных пользователя в базе данных."""
        try:
            user = await self.get_user_or_404(db=db, username=username)
            hashed_password = user.hashed_password
            if new_user_data.password:
                self._check_password_complexity(new_user_data.password)
                hashed_password = create_hash(new_user_data.password)
            username = user.username
            if new_user_data.username:
                self._validate_username(new_user_data.username)
                username = new_user_data.username
            email = new_user_data.email or user.email
            first_name = new_user_data.first_name or user.first_name
            last_name = new_user_data.last_name or user.last_name
            is_active = (
                new_user_data.is_active
                if new_user_data.is_active is not None
                else user.is_active
            )
            # обновляем дату изменения
            modified_at = datetime.utcnow()
            user_in_db = UserInDBBase(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                hashed_password=hashed_password,
                is_active=is_active,
                created_at=user.created_at,
                modified_at=modified_at,
            )
            updated_user = await self.db_service.update(
                db=db, db_obj=user, obj_in=user_in_db
            )
            return updated_user
        except IntegrityError as exc:
            self._handle_integrity_error(exc, new_user_data)

    def _handle_integrity_error(
        self, exc: IntegrityError, user_data: UserCreate
    ) -> None:
        """Обработка ошибки IntegrityError."""
        if "users_email_key" in str(exc):
            raise EmailAlreadyUsedException(user_data.email) from exc
        if "users_username_key" in str(exc):
            raise UsernameAlreadyExistException(user_data.username) from exc

    def _check_password_complexity(self, password: str) -> None:
        """Проверка сложности пароля перед хэшированием."""
        if not (
            (settings.min_password_input_length - 1)
            < len(password)
            < (settings.max_password_input_length + 1)
        ):
            raise PasswordComplexityException

    def _validate_username(self, username: str) -> None:
        """Исключение недопустимого имени."""
        if username.lower() == "me":
            raise UsernameNotMeException(username)
        username_pattern = re.compile(settings.username_pattern)
        if not username_pattern.match(username):
            raise NotAllowedUsernameException

    def _create_user_in_db_full_compact_roles(
        self, user: User, is_admin_request: bool
    ) -> UserInDBFull:
        roles = user.roles
        if not is_admin_request:
            roles = [
                role
                for role in user.roles
                if role.is_active
                and (not role.expire_at or role.expire_at > datetime.utcnow())
            ]

        user_in_db_full_compact_roles = UserInDBFull(
            username=user.username,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            created_at=user.created_at,
            modified_at=user.modified_at,
            id=user.id,
            hashed_password=user.hashed_password,
            is_active=user.is_active,
            roles=[
                RoleInDWithExpireAt(
                    title=role.role.title,
                    description=role.role.description,
                    id=role.id,
                    created_at=role.created_at,
                    modified_at=role.modified_at,
                    expire_at=role.expire_at,
                    is_active=role.is_active,
                )
                for role in roles
            ],
        )
        return user_in_db_full_compact_roles

    def get_data_to_delete_user(self, user: UserInDBBase) -> UserAdminUpdate:
        """Получение подменных данных для удаляемого пользователя."""
        username = create_hash(user.username)
        adress, domain = user.email.split("@", 1)
        hashed_adress = create_hash(adress)
        max_adress_len = settings.max_email_length - len(f"@{domain}")
        hashed_adress = hashed_adress[:max_adress_len]
        email = f"{hashed_adress}@{domain}"
        first_name = create_hash(user.first_name)
        last_name = create_hash(user.last_name)
        update_data = UserAdminUpdate(
            username=username[: settings.max_username_length],
            email=email,
            first_name=first_name[: settings.max_first_name_length],
            last_name=last_name[: settings.max_last_name_length],
            is_active=False,
        )
        return update_data

    async def _check_social_account_bounded(
        self, db: AsyncSession, user: User, reg_data: BaseUserSocialNetwork
    ) -> UserInDBFull | None:
        # проверяем наличие привязки существующего аккаунта к соцсети
        stmt = select(SocialAccount).where(
            SocialAccount.user_id == user.id,
            SocialAccount.social_id == reg_data.social_id,
            SocialAccount.social_name == reg_data.social_name,
        )
        result = await self.db_service.execute(db=db, stmt=stmt)
        already_registred = result.unique().scalars().first()
        if already_registred:
            return user
        return None

    async def get_user_data_from_yandex(
        self, code: str
    ) -> BaseUserSocialNetwork:
        try:
            # Формируем тело запроса
            data = {
                "grant_type": "authorization_code",
                "code": code,
            }
            secrets = (
                f"{settings.yandex_client_id}:{settings.yandex_client_secret}"
            )
            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "Authorization": (
                    f"Basic {base64.b64encode(secrets.encode()).decode()}"
                ),
            }
            # делаем запрос на получение токена Яндекс

            response = await httpx.AsyncClient().post(
                settings.yandex_token_url, data=data, headers=headers
            )
            if response.headers["content-type"] == "application/json":
                try:
                    token = response.json()
                except JSONDecodeError as exc:
                    raise exc
            else:
                raise Exception

            # делаем запрос на получение данных пользователя
            access_token = token["access_token"]
            yandex_login_headers = {"Authorization": access_token}
            user_data = await httpx.AsyncClient().get(
                settings.yandex_login_url, headers=yandex_login_headers
            )
            # парсим полученный ответ
            reg_data = BaseUserSocialNetwork(
                username=user_data["login"],
                email=user_data["default_email"],
                social_id=user_data["id"],
                first_name=user_data["first_name"],
                last_name=user_data["last_name"],
                social_name=SocialNetworks.yandex,
            )
            return reg_data
        except OAuthError as exc:
            raise exc


class UserHistoryService:
    def __init__(self, db_service: Type[DBService]):
        self.db_service = db_service()

    async def create_user_history_in_db(
        self,
        db: AsyncSession,
        user_id: UUID,
        user_agent: str,
        activity: str,
    ) -> None:
        db_obj_h = UserHistoryInDB(
            user_id=user_id,
            user_agent=user_agent,
            activity=activity,
        )
        await self.db_service.create(db=db, obj_in=db_obj_h)

    async def get_user_history(
        self, db: AsyncSession, current_user: BaseUser, page_params: PageParams
    ) -> list[UserHistory]:
        history_db = await self.db_service.get_list(
            db=db,
            filters=dict(user_id=current_user.id),
            offset=page_params.offset,
            limit=page_params.limit,
        )
        history = [UserHistory.model_validate(row) for row in history_db]
        return history


class UserSocialAccountService:
    def __init__(self, db_service: Type[DBService]):
        self.db_service = db_service()

    async def create_user_social_account_in_db(
        self,
        db: AsyncSession,
        user: UserInDBFull,
        reg_data: BaseUserSocialNetwork,
    ) -> None:
        try:
            social_account = SocialAccountInDB(
                user_id=user.id,
                social_id=reg_data.social_id,
                social_name=reg_data.social_name,
            )
            await self.db_service.create(db=db, obj_in=social_account)
        except IntegrityError as exc:
            raise USserAlreadyBoundedToSocialNetworkException(
                social_account.social_name
            ) from exc

    async def unbound_user_from_social_account_in_db(
        self,
        db: AsyncSession,
        user: UserInDBFull,
    ) -> None:
        user_id = SocialAccountUserId(user_id=user.id)
        result = await self.db_service.delete(db=db, obj=user_id)
        if not result:
            raise UserHaveNotBoundedException


@lru_cache()
def get_user_service() -> UserService:
    return UserService(UserDBService)


@lru_cache()
def get_user_history_service() -> UserHistoryService:
    return UserHistoryService(UserHistoryDBService)


@lru_cache()
def get_user_social_account_service() -> UserSocialAccountService:
    return UserSocialAccountService(UserSocialAccountDBService)
