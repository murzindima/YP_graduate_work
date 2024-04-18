from datetime import timedelta, datetime
from functools import lru_cache
from typing import Callable, Type
from uuid import UUID

from jose import jwt, JWTError, ExpiredSignatureError
from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, ValidationError
from sqlalchemy.ext.asyncio import AsyncSession


from core.config import settings, RightsName
from core.exceptions import (
    RulesException,
    CredentialsException,
    LoginException,
    TokenExpiredException,
    TokenNonExistentException,
    UserInactiveException,
    ValidationException,
    ProcessErrorException,
)
from db.postgres import get_session
from models.token import UserRefreshToken
from schemas.token_schema import (
    ActiveStatus,
    oauth2_scheme,
    RefreshTokenInDB,
    RefreshToken,
    Tokens,
)
from schemas.user_schema import UserInDBFull
from services.db_service import DBService, SQLAlchemyDBService
from services.cache import get_cache_service, RedisCacheService
from services.utils import check_password
from services.user_service import (
    get_user_history_service,
    get_user_service,
)


class TokenDBService(SQLAlchemyDBService):
    model = UserRefreshToken


class TokenService:
    def __init__(self, db_service: Type[DBService]):
        self.db_service = db_service()
        self.user_service = get_user_service()
        self.user_history_service = get_user_history_service()

    async def authenticate_user(
        self,
        db: AsyncSession,
        form_data: OAuth2PasswordRequestForm,
        user_agent: str,
    ) -> Tokens:
        """Проводим аутентификацию пользователя."""
        user = await self.user_service.get_user_or_404(
            db=db, username=form_data.username
        )
        if not user or not check_password(
            form_data.password, user.hashed_password
        ):
            raise LoginException
        if not user.is_active:
            raise UserInactiveException
        # получаем токены
        tokens = await self.get_tokens(db=db, user=user, user_agent=user_agent)
        return tokens

    async def revoke_tokens(
        self,
        db: AsyncSession,
        token: str,
        refresh_token: str,
        cache: RedisCacheService,
        user_agent: str,
    ) -> None:
        """Отзываем токены."""
        current_user = await self.get_current_user(
            db=db, token=token, cache=cache
        )
        token_obj = await self._get_refresh_token_from_db(
            db=db, obj=RefreshToken(token=refresh_token)
        )
        username_from_refresh_token = self._get_username_from_token(
            token=refresh_token, refresh=True
        )
        if username_from_refresh_token != current_user.username:
            raise ValidationException("user from refresh token")
        # заносим отозванный access токен в кэш и проверяем
        await cache.add_to_set(
            key=str(current_user.id),
            value=token,
            expire_sec=settings.access_token_expire_minutes * 60,
        )
        result_for_access_token = await cache.is_value_in_set(
            key=str(current_user.id), value=token, cache=cache
        )
        # проверяем результат отзыва refresh токена (успешно - это False !)
        is_active_refresh_token = await self._set_token_status(
            db=db, token_obj=token_obj, status=False
        )
        is_revoked = all(
            [result_for_access_token, not is_active_refresh_token]
        )
        if not is_revoked:
            raise ProcessErrorException
        await self.user_history_service.create_user_history_in_db(
            db=db,
            user_id=current_user.id,
            user_agent=user_agent,
            activity="logout",
        )

    async def refresh_tokens(
        self, db: AsyncSession, refresh_token: str, user_agent: str
    ) -> Tokens:
        """Генерируем новую пару токенов, если refresh token валиден и не истек."""

        # проверяем действительность refresh токена
        token_obj = await self._get_refresh_token_from_db(
            db=db, obj=RefreshToken(token=refresh_token)
        )
        username = self._get_username_from_token(
            token=refresh_token, refresh=True
        )
        user = await self.user_service.get_user_or_404(
            db=db, username=username
        )
        # получаем новую пару токенов
        tokens = await self.get_tokens(db=db, user=user, user_agent=user_agent)

        # отзываем refresh токен после использования
        await self._set_token_status(db=db, token_obj=token_obj, status=False)
        return tokens

    async def get_current_user(
        self,
        db: AsyncSession,
        token: str,
        cache: RedisCacheService,
    ) -> UserInDBFull:
        """Получаем текущего пользователя с действующим токеном."""
        payload = self.get_payload(token=token)
        user_id = payload.get("user_id")
        await self._has_revoked_access_token(
            user_id=UUID(user_id), access_token=token, cache=cache
        )
        username = self._get_username_from_token(token=token)
        user = await self.user_service.get_user_or_404(
            db=db, username=username
        )
        if not user.is_active:
            raise UserInactiveException
        return user

    async def _has_revoked_access_token(
        self, user_id: UUID, access_token: str, cache: RedisCacheService
    ) -> None:
        """Проверяем, отозван ли access токен у пользователя (True - отозван)."""

        is_value = await cache.is_value_in_set(
            key=str(user_id), value=access_token
        )
        if is_value:
            raise CredentialsException

    def _create_token(
        self,
        data: dict,
        expires_delta: timedelta,
        secret_key: str = settings.access_token_secret_key,
    ) -> str:
        """Создаем токен (access или refresh)."""
        to_encode = data.copy()
        expire = datetime.utcnow() + expires_delta
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode,
            secret_key,
            algorithm=settings.token_jwt_algorithm,
        )
        return encoded_jwt

    def _get_username_from_token(
        self, token: str, refresh: bool = False
    ) -> str:
        """Получаем пользователя по refresh токену."""
        payload = self.get_payload(token=token, refresh=refresh)
        username = payload.get("username")
        return str(username)

    async def _create_refresh_token_in_db(
        self, db: AsyncSession, token_in_db: RefreshTokenInDB
    ):
        """Создаем в базе данных запись с новым refresh токеном."""
        new_token = await self.db_service.create(
            db=db,
            obj_in=token_in_db,
        )
        return new_token

    async def _set_token_status(
        self, db: AsyncSession, token_obj: UserRefreshToken, status: bool
    ) -> bool:
        """Меняем для токена статус is_active на False (отзываем)"""
        token = await self.db_service.update(
            db=db, db_obj=token_obj, obj_in=ActiveStatus(is_active=status)
        )
        return token.is_active

    async def _get_refresh_token_from_db(
        self, db: AsyncSession, obj: BaseModel
    ) -> UserRefreshToken:
        """Получаем объект действующего refresh токен из БД."""

        token_obj = await self.db_service.get(db=db, obj=obj)
        if not token_obj or not token_obj.is_active:
            raise TokenNonExistentException
        return token_obj

    async def get_tokens(
        self, db: AsyncSession, user: UserInDBFull, user_agent: str
    ) -> dict[str, str]:
        """Получаем access и refresh токены."""
        roles = [role.title for role in user.roles] if user.roles else []
        data = {
            "username": user.username,
            "user_id": str(user.id),
            "roles": roles,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
        }
        access_token_expires = timedelta(
            minutes=settings.access_token_expire_minutes
        )
        access_token = self._create_token(
            data=data,
            expires_delta=access_token_expires,
        )
        refresh_token_expires = timedelta(
            days=settings.refresh_token_expire_days
        )
        refresh_token = self._create_token(
            data=data,
            expires_delta=refresh_token_expires,
            secret_key=settings.refresh_token_secret_key,
        )
        # заносим refresh токен в базу данных
        token_in_db = RefreshTokenInDB(
            user_id=user.id,
            token=refresh_token,
            expire_at=datetime.utcnow() + refresh_token_expires,
        )
        await self._create_refresh_token_in_db(db=db, token_in_db=token_in_db)
        # записываем в историю факт входа в аккаунт
        await self.user_history_service.create_user_history_in_db(
            db=db, user_id=user.id, user_agent=user_agent, activity="login"
        )
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "tokens_type": "bearer",
        }

    def get_payload(self, token: str, refresh: bool = False) -> dict:
        try:
            secret_key = settings.access_token_secret_key
            if refresh:
                secret_key = settings.refresh_token_secret_key
            payload = jwt.decode(
                token,
                secret_key,
                algorithms=settings.token_jwt_algorithm,
            )
            user_id = payload.get("user_id")
            if user_id is None:
                raise CredentialsException
            username = payload.get("username")
            if username is None:
                raise CredentialsException
            return payload
        except ExpiredSignatureError as exc:
            raise TokenExpiredException from exc
        except (JWTError, ValidationError) as exc:
            raise ValidationException(refresh) from exc


@lru_cache()
def get_user_token_service() -> TokenService:
    return TokenService(TokenDBService)


def check_rights(status: str | None = None) -> Callable:
    async def get_request_user(
        db: AsyncSession = Depends(get_session),
        token: str = Depends(oauth2_scheme),
        token_service: TokenService = Depends(get_user_token_service),
        cache: RedisCacheService = Depends(get_cache_service),
    ) -> UserInDBFull:
        payload = token_service.get_payload(token=token)
        roles = payload.get("roles")
        if isinstance(roles, list) and RightsName.admin in roles:
            current_user = await token_service.get_current_user(
                db=db, token=token, cache=cache
            )
            return current_user
        if not status:
            current_user = await token_service.get_current_user(
                db=db, token=token, cache=cache
            )
            return current_user
        if isinstance(roles, list) and status not in roles:
            raise RulesException
        current_user = await token_service.get_current_user(
            db=db, token=token, cache=cache
        )
        return current_user

    return get_request_user
