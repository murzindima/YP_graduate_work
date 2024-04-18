from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from pydantic import BaseModel
from sqlalchemy import and_, delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from db.postgres import Base


class DBService(ABC):
    @abstractmethod
    async def create(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    async def delete(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    async def execute(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    async def get(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    async def get_list(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    async def update(self, *args, **kwargs):
        raise NotImplementedError


ModelType = TypeVar("ModelType", bound=Base)
DBFieldsType = TypeVar("DBFieldsType", bound=BaseModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
DeleteSchemaType = TypeVar("DeleteSchemaType", bound=BaseModel)
ExecuteSchemaType = TypeVar("ExecuteSchemaType", bound=BaseModel)
GetSchemaType = TypeVar("GetSchemaType", bound=BaseModel)
GetListSchemaType = TypeVar("GetListSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class SQLAlchemyDBService(
    DBService,
    Generic[
        ModelType,
        DBFieldsType,
        CreateSchemaType,
        DeleteSchemaType,
        ExecuteSchemaType,
        GetSchemaType,
        GetListSchemaType,
        UpdateSchemaType,
    ],
):
    model = Base

    async def create(
        self, db: AsyncSession, obj_in: CreateSchemaType
    ) -> ModelType:
        obj_in_data = obj_in.model_dump()
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def delete(self, db: AsyncSession, obj: DBFieldsType):
        obj = obj.model_dump()
        conditions = [getattr(self.model, k) == v for k, v in obj.items()]
        stmt = (
            delete(self.model).where(and_(*conditions)).returning(self.model)
        )
        result = await db.execute(statement=stmt)
        await db.commit()
        return result.scalar_one_or_none()

    async def execute(self, db: AsyncSession, stmt):
        result = await db.execute(statement=stmt)
        return result

    async def get(
        self, db: AsyncSession, obj: DBFieldsType
    ) -> ModelType | None:
        obj = obj.model_dump()
        conditions = [getattr(self.model, k) == v for k, v in obj.items()]
        stmt = select(self.model).where(and_(*conditions))
        result = await db.execute(statement=stmt)
        return result.scalar_one_or_none()

    async def get_list(
        self,
        db: AsyncSession,
        filters: dict | None = None,
        offset: int = 0,
        limit: int | None = None,
    ) -> list[ModelType]:
        if not filters:
            filters = {}
        conditions = [getattr(self.model, k) == v for k, v in filters.items()]
        stmt = select(self.model).where(and_(*conditions)).offset(offset)
        if limit:
            stmt = stmt.limit(limit)
        results = await db.execute(stmt)
        return results.scalars().all()

    async def update(
        self,
        db: AsyncSession,
        db_obj: ModelType,
        obj_in: UpdateSchemaType,
    ) -> ModelType | None:
        obj_in_dump = obj_in.model_dump()
        stmt = (
            update(self.model)
            .where(self.model.id == str(db_obj.id))
            .values(**obj_in_dump)
        )
        await db.execute(stmt)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
