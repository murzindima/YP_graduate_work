from typing import Any

from fastapi import Depends

from models.favourites import Favourite
from core.exceptions import ObjectDoesNotExistExeption
from services.mongo_storage import MongoStorage, get_favourites_storage


class FavouritesService:
    def __init__(self, collection: MongoStorage) -> None:
        self.collection = collection

    async def create_favourite(
        self, favourite: Favourite, user_id
    ) -> Favourite:
        if await self._check_object_exists({'user_id': user_id}):
            filter = {'user_id': user_id}
            data = {
                '$addToSet': {'favourites': favourite.model_dump()}}
            await self.collection.upsert_one(filter, data)
        else:
            filter = {'user_id': {'$ne': user_id}}
            data = {
                '$set': {'user_id':  user_id},
                '$addToSet': {'favourites': favourite.model_dump()}}
            await self.collection.upsert_one(filter, data)
        return favourite

    async def delete_favourite(self, film_id: str, user_id: str) -> str:
        filter_criteria = {'user_id': user_id,
                           'favourites.film_id': film_id}
        update_data = {'$pull': {'favourites': {'film_id': film_id}}}
        return await self.collection.upsert_one(filter_criteria, update_data)

    async def get_user_favourites(self, user_id: str) -> dict[Any, Any]:
        favourite = await self.collection.get_by_id(
            filters={'user_id': user_id},
        )
        if not favourite:
            raise ObjectDoesNotExistExeption
        return favourite

    async def get_all_favourites(self) -> list[dict[Any, Any]]:
        fav = await self.collection.get_list({})
        return fav

    async def _check_object_exists(self, filter) -> bool:
        result = await self.collection.get_by_id(filter)
        return result is not None


def get_favourites_service(
    collection: MongoStorage = Depends(get_favourites_storage),
) -> FavouritesService:
    return FavouritesService(collection=collection)
