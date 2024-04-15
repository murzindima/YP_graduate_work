from fastapi import Depends
from pymongo.collection import ObjectId
from pymongo.errors import DuplicateKeyError, WriteError

from core.helpers import form_mongo_update_data
from core.exceptions import ObjectDoesNotExistExeption
from models.films import Like, LikeCreate
from services.mongo_storage import MongoStorage, get_film_storage


class LikeService:
    def __init__(self, collection: MongoStorage) -> None:
        self.collection = collection

    async def like_movie(
        self, movie_id: str, user_id: str, like: LikeCreate
    ) -> Like:
        like_db = Like(user_id=user_id, **like.model_dump())
        if not await self.collection.get_by_id({'_id': ObjectId(movie_id)}):
            raise ObjectDoesNotExistExeption
        try:
            id = {'_id': ObjectId(movie_id), 'likes.user_id': {'$ne': user_id}}
            data = {'$addToSet': {'likes': like_db.model_dump()}}
            await self.collection.upsert_one(id, data)
        except DuplicateKeyError:
            id = {'_id': ObjectId(movie_id), 'likes.user_id': user_id}
            form_data = form_mongo_update_data(like_db, 'likes.$.')
            data = {'$set': form_data}
            await self.collection.upsert_one(id, data)
        return like_db

    async def like_review(
        self, movie_id: str, review_id: str, user_id: str, like: LikeCreate
    ) -> Like:
        like_db = Like(user_id=user_id, **like.model_dump())
        if not await self.collection.get_by_id(
            {'_id': ObjectId(movie_id),
             'reviews.review_id': review_id}):
            raise ObjectDoesNotExistExeption
        try:
            id = {
                '_id': ObjectId(movie_id),
                'reviews.review_id': review_id,
                'reviews': {'$elemMatch': {'likes.user_id': {'$ne': user_id}}},
            }
            data = {'$addToSet': {'reviews.$.likes': like_db.model_dump()}}
            await self.collection.upsert_one(id, data)
        except WriteError:
            id = {
                '_id': ObjectId(movie_id),
                'reviews.review_id': review_id,
                'reviews.likes.user_id': user_id,
            }
            form_data = form_mongo_update_data(
                like_db, 'reviews.$[outer].likes.$[inner].'
            )
            data = {'$set': form_data}
            array_filters = [
                {'outer.review_id': review_id},
                {'inner.user_id': user_id},
            ]
            await self.collection.upsert_one(id, data, array_filters)
        return like_db

    async def remove_like_from_movie(self, movie_id: str, user_id: str) -> ObjectId:
        filter_criteria = {'_id': ObjectId(movie_id)}
        update_data = {'$pull': {'likes': {'user_id': user_id}}}
        return await self.collection.upsert_one(filter_criteria, update_data)

    async def remove_like_from_review(
        self, movie_id: str, review_id: str, user_id: str
    ) -> ObjectId:
        filter_criteria = {
            '_id': ObjectId(movie_id),
            'reviews.review_id': review_id,
        }
        update_data = {'$pull': {'reviews.$.likes': {'user_id': user_id}}}
        return await self.collection.upsert_one(filter_criteria, update_data)


def get_like_service(
    collection: MongoStorage = Depends(get_film_storage),
) -> LikeService:
    return LikeService(collection=collection)
