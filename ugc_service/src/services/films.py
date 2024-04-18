from fastapi import Depends
from typing import Any

from core.exceptions import ObjectDoesNotExistExeption, DuplicateObjectExeption
from models.films import MovieCreate, MovieInDb
from services.mongo_storage import MongoStorage, get_film_storage


class FilmService:
    def __init__(self, collection: MongoStorage) -> None:
        self.collection = collection

    async def get_movie(self, data: str) -> dict:
        result = await self.collection.get_by_id({'_id': data})
        if not result:
            raise ObjectDoesNotExistExeption
        return result

    async def create_movie(self, movie: MovieCreate) -> MovieInDb:
        id = {'_id': movie.id}
        data = {
            '$setOnInsert': movie.model_dump(),
        }
        movie_id = await self.collection.upsert_one(id, data)
        if not movie_id:
            raise DuplicateObjectExeption
        movie_db = MovieInDb(_id=movie_id, **movie.model_dump())
        return movie_db

    async def get_movies(self) -> list[dict[Any, Any]]:
        movies = await self.collection.get_list({})
        return movies

    async def delete_movie(self, movie_id):
        return await self.collection.delete_one(movie_id)

    async def get_user_likes(self, user_id):
        movies = await self.collection.get_list(
            {"likes.user_id": user_id}, {"_id": 1})
        return [doc["_id"] for doc in movies]


def get_film_service(
    collection: MongoStorage = Depends(get_film_storage),
) -> FilmService:
    return FilmService(collection=collection)
