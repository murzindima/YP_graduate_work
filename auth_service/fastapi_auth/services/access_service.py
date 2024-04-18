"""Сервис управление доступом"""

from datetime import datetime
from functools import lru_cache
from typing import Type

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from core.exceptions import (
    UserRoleNotFoundException,
    OverrideUserRoleException,
    SelfDeleteAdminUserRoleException,
)
from models.common import UserRoleModel
from schemas.mixins import IdMixinSchema
from schemas.role_schema import RoleTitle
from schemas.user_role_schema import (
    UserRoleSchema,
    UserRoleInDBSchema,
    UserRoleChange,
    UserRoleAssign,
)
from schemas.user_schema import UserInDBFull
from services.db_service import DBService, SQLAlchemyDBService
from services.role_service import get_role_service
from services.user_service import get_user_service


class AccessDBService(SQLAlchemyDBService):
    model = UserRoleModel


class AccessService:
    def __init__(self, db_service: Type[DBService]):
        self.db_service = db_service()
        self.role_service = get_role_service()
        self.user_service = get_user_service()

    async def assign_user_role(
        self,
        db: AsyncSession,
        username: str,
        role_data: UserRoleAssign,
    ) -> None:
        """Назначение роли пользователю"""
        try:
            user = await self.user_service.get_user_or_404(
                db=db, username=username
            )
            role_obj = RoleTitle(title=role_data.title)
            role = await self.role_service.get(db=db, role=role_obj)
            is_active = True
            if role_data.is_active is not None:
                is_active = role_data.is_active
            role_data = UserRoleSchema(
                role_id=role.id,
                user_id=user.id,
                expire_at=role_data.expire_at or None,
                is_active=is_active,
            )
            await self.db_service.create(db=db, obj_in=role_data)
        except IntegrityError:
            raise OverrideUserRoleException

    async def get_user_role(
        self, db: AsyncSession, username: str, role_title: str
    ) -> UserRoleInDBSchema:
        """Получение роли пользователя."""
        user = await self.user_service.get_user_or_404(
            db=db, username=username
        )
        role_obj = RoleTitle(title=role_title)
        role = await self.role_service.get(db=db, role=role_obj)
        stmt = select(UserRoleModel).where(
            UserRoleModel.user_id == user.id, UserRoleModel.role_id == role.id
        )
        result = await self.db_service.execute(db=db, stmt=stmt)
        user_role = result.unique().scalars().first()
        if not user_role:
            raise UserRoleNotFoundException
        return user_role

    async def get_user_role_list(
        self, db: AsyncSession, username: str, page_number: int, page_size: int
    ) -> list[UserRoleInDBSchema]:
        """Получение ролей пользователя по username."""
        user = await self.user_service.get_user_or_404(
            db=db, username=username
        )
        user_list = await self.db_service.get_list(
            db=db,
            offset=(page_number - 1) * page_size,
            limit=page_size,
            filters={"user_id": user.id},
        )
        return user_list

    async def update_user_role(
        self,
        db: AsyncSession,
        username: str,
        role_title: str,
        new_user_role_data: UserRoleChange,
    ) -> UserRoleInDBSchema:
        """Изменение роли пользователя."""
        user_role = await self.get_user_role(
            db=db, username=username, role_title=role_title
        )
        is_active = user_role.is_active
        if new_user_role_data.is_active is not None:
            is_active = new_user_role_data.is_active
        obj_in = UserRoleInDBSchema(
            role_id=user_role.role_id,
            user_id=user_role.user_id,
            is_active=is_active,
            expire_at=new_user_role_data.expire_at or user_role.expire_at,
            created_at=user_role.created_at,
            modified_at=datetime.utcnow(),
            id=user_role.id,
        )
        result = await self.db_service.update(
            db=db, db_obj=user_role, obj_in=obj_in
        )
        return result

    async def remove_user_role(
        self,
        db: AsyncSession,
        username: str,
        role_title: str,
        admin_user: UserInDBFull,
    ) -> None:
        """Удаление роли у пользователя"""
        user_role = await self.get_user_role(
            db=db, username=username, role_title=role_title
        )
        if user_role.user_id == admin_user.id:
            raise SelfDeleteAdminUserRoleException
        obj = IdMixinSchema(id=user_role.id)
        await self.db_service.delete(db=db, obj=obj)


@lru_cache()
def get_access_service() -> AccessService:
    return AccessService(AccessDBService)
