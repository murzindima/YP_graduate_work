from abc import ABC, abstractmethod

from bson import ObjectId
from fastapi import Depends

from db.mongo import get_mongodb


class AbstractStorage(ABC):
    def __init__(self, collection):
        """
        Инициализирует сервис для взаимодействия с коллекцией.
        """
        self.collection = collection

    @abstractmethod
    async def insert(self, data: dict) -> ObjectId:
        """
        Вставляет новый документ в коллекцию и возвращает вставленный документ.

        :param data: dict - данные для вставки
        :return: dict - вставленный документ
        """
        pass

    @abstractmethod
    async def upsert_one(
        self, filter: dict, data: dict, array_filters: list = []
    ) -> ObjectId:
        """
        Обновляет документ в коллекции по заданным параметрам или вставляет новый, если не найден.

        :param data: dict - данные для обновления или вставки
        :return: None
        """
        pass

    @abstractmethod
    async def get_list(
        self,
        filters: dict,
        projection: dict = {},
        skip: int = 0,
        limit: int = 100,
    ) -> list[dict]:
        """
        Выполняет поиск документов в коллекции с использованием заданного фильтра, пропускает
        указанное количество документов и возвращает список документов на указанной странице.

        :param filter_: dict - фильтр для поиска
        :param page_number: int - номер страницы
        :param page_size: int - размер страницы
        :return: list[dict] - список документов на указанной странице
        """
        pass

    @abstractmethod
    async def get_by_id(self, filters: dict, projection: dict = {},) -> dict:
        """
        Возвращает документ из коллекции по заданному идентификатору.

        :param id_: str - идентификатор документа
        :return: dict - найденный документ или None, если не найден
        """
        pass

    @abstractmethod
    async def delete_one(self, id_: str) -> int:
        """
        Удаляет документ из коллекции по заданному идентификатору и возвращает количество удаленных документов.

        :param id_: str - идентификатор документа для удаления
        :return: int - количество удаленных документов (обычно 0 или 1)
        """
        pass


class MongoStorage(AbstractStorage):
    async def insert(self, data: dict) -> ObjectId:
        result = await self.collection.insert_one(data, upsert=True)
        return result.inserted_id

    async def upsert_one(
        self, filter: dict, data: dict, array_filters: list = []
    ) -> ObjectId:
        result = await self.collection.update_one(
            filter, data, upsert=True, array_filters=array_filters
        )
        return result.upserted_id if result.upserted_id else None

    async def get_list(
        self,
        filters: dict,
        projection: dict = {},
        skip: int = 0,
        limit: int = 100,
    ) -> list[dict]:
        cursor = (
            self.collection.find(filters, projection).skip(skip).limit(limit)
        )
        docs = await cursor.to_list(length=None)
        return docs

    async def get_by_id(self, filters: dict, projection: dict = {},) -> dict:
        doc = await self.collection.find_one(filters, projection)
        return doc if doc else None

    async def delete_one(self, id_: str) -> int:
        filters = {'_id': ObjectId(id_)}
        result = await self.collection.delete_one(filters)
        return result.deleted_count


def get_favourites_storage(
    collection=Depends(get_mongodb),
) -> MongoStorage:
    collection = collection['ugc']['favourites']
    return MongoStorage(collection=collection)


def get_film_storage(
    collection=Depends(get_mongodb),
) -> MongoStorage:
    collection = collection['ugc']['movies']
    return MongoStorage(collection=collection)
