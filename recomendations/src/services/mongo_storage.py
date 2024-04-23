from abc import ABC, abstractmethod

from fastapi import Depends

from db.mongo import get_mongodb


class AbstractStorage(ABC):
    def __init__(self, collection):
        """
        Инициализирует сервис для взаимодействия с коллекцией.
        """
        self.collection = collection

    @abstractmethod
    async def get_list(self) -> list[dict]:
        """
        Выполняет поиск документов в коллекции и возвращает список документов.
        :return: list[dict] - список документов
        """
        pass

    @abstractmethod
    async def insert_many(
        self,
        data: list[dict],
    ) -> dict:
        """
        Добавляет список документов в коллекцию.

        :param data: list[dict] - список документов для добавления
        :return: None
        """
        pass

    @abstractmethod
    async def delete_all(self) -> None:
        """
        Удаляет все документы из коллекции.

        :return: None
        """
        pass


class MongoStorage(AbstractStorage):
    async def get_list(self) -> list[dict]:
        cursor = self.collection.find()
        docs = await cursor.to_list(length=None)
        return docs

    async def insert_many(self, data: list[dict]) -> None:
        await self.collection.insert_many(data)

    async def delete_all(self) -> None:
        await self.collection.delete_many({})


def get_user_movie_storage(
    collection=Depends(get_mongodb),
) -> MongoStorage:
    collection = collection["movie_recommender"]["user_movie_matrix"]
    return MongoStorage(collection=collection)


def get_similarity_storage(
    collection=Depends(get_mongodb),
) -> MongoStorage:
    collection = collection["movie_recommender"]["user_similarity"]
    return MongoStorage(collection=collection)


def get_new_movies_storage(
    collection=Depends(get_mongodb),
) -> MongoStorage:
    collection = collection["movie_recommender"]["new_movies"]
    return MongoStorage(collection=collection)
