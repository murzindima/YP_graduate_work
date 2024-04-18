"""Сервис CRUD для ролей доступа"""

from datetime import datetime
from functools import lru_cache
from typing import Type

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select


from core.config import RightsName
from core.exceptions import (
    OverrideRoleException,
    RoleNotFoundException,
    AdminRoleDeleteException,
    AdminRoleNameChangeException,
    BoundedToUserRoleException,
)
from models.common import Role, UserRoleModel
from schemas.role_schema import (
    RoleBase,
    RoleInDB,
    RoleTitle,
    RoleUpdate,
    RoleInDBFull,
)
from services.db_service import DBService, SQLAlchemyDBService


class RoleDBService(SQLAlchemyDBService):
    model = Role


class RoleService:
    def __init__(
        self,
        db_service: Type[DBService],
    ) -> None:
        self.db_service = db_service()

    async def create(self, db: AsyncSession, role: RoleBase) -> RoleInDB:
        try:
            result = await self.db_service.create(db=db, obj_in=role)
            return result
        except IntegrityError as e:
            raise OverrideRoleException from e

    async def get(self, db: AsyncSession, role: RoleTitle) -> RoleInDBFull:
        role = await self.db_service.get(db=db, obj=role)
        if not role:
            raise RoleNotFoundException
        return role

    async def get_role_list(
        self, db: AsyncSession, page_number: int, page_size: int
    ) -> list[RoleInDB]:
        """Получаем список ролей с пагинацией."""
        role_list = await self.db_service.get_list(
            db=db, offset=(page_number - 1) * page_size, limit=page_size
        )
        return role_list

    async def update(
        self, db: AsyncSession, role: RoleTitle, updated_role_data: RoleUpdate
    ) -> RoleInDB:
        try:
            if (
                role.title == RightsName.admin
                and updated_role_data.title != role.title
            ):
                raise AdminRoleNameChangeException
            role = await self.get(db=db, role=role)
            title = updated_role_data.title or role.title
            description = updated_role_data.description or role.description
            modified_at = datetime.utcnow()
            obj_in = RoleInDBFull(
                title=title,
                description=description,
                id=role.id,
                created_at=role.created_at,
                modified_at=modified_at,
            )
            result = await self.db_service.update(
                db=db, db_obj=role, obj_in=obj_in
            )
            return result
        except IntegrityError as e:
            raise OverrideRoleException from e

    async def delete(self, db: AsyncSession, role: RoleTitle) -> None:
        if role.title == RightsName.admin:
            raise AdminRoleDeleteException
        # проверяем наличие записей роль-пользователь
        role_from_db = await self.get(db=db, role=role)
        stmt = select(UserRoleModel).where(
            UserRoleModel.role_id == role_from_db.id
        )
        result = await self.db_service.execute(db=db, stmt=stmt)
        user_role_list = result.scalars().all()
        if len(user_role_list) > 0:
            raise BoundedToUserRoleException(role.title)
        await self.db_service.delete(db=db, obj=role)


@lru_cache()
def get_role_service() -> RoleService:
    return RoleService(db_service=RoleDBService)
