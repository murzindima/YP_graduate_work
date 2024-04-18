from uuid import uuid4

from fastapi import Depends
from pymongo.errors import DuplicateKeyError

from core.helpers import form_mongo_update_data
from core.exceptions import ObjectDoesNotExistExeption
from models.films import Review, ReviewCreate
from services.mongo_storage import MongoStorage, get_film_storage


class ReviewService:
    def __init__(self, collection: MongoStorage) -> None:
        self.collection = collection

    async def add_review(
        self, movie_id: str, user_id: str, review: ReviewCreate
    ) -> Review:
        review_db = Review(
            user_id=user_id, review_id=str(uuid4()), **review.model_dump()
        )
        if not await self.collection.get_by_id({'_id': movie_id}):
            raise ObjectDoesNotExistExeption
        try:
            id = {
                '_id': movie_id,
                'reviews.user_id': {'$ne': user_id},
            }
            data = {'$addToSet': {'reviews': review_db.model_dump()}}
            await self.collection.upsert_one(id, data)
        except DuplicateKeyError:
            id = {'_id': movie_id, 'reviews.user_id': user_id}
            form_data = form_mongo_update_data(review_db, 'reviews.$.')
            data = {'$set': form_data}
            await self.collection.upsert_one(id, data)
        return review_db

    async def remove_review_from_movie(
        self, movie_id: str, review_id: str
    ) -> str:
        filter_criteria = {'_id': movie_id}
        update_data = {'$pull': {'reviews': {'review_id': review_id}}}
        return await self.collection.upsert_one(filter_criteria, update_data)

    async def get_movie_reviews(self, movie_id: str) -> list[Review]:
        filters = {'_id': movie_id}
        projection = {'reviews': 1, '_id': 0}
        reviews = await self.collection.get_by_id(filters, projection)
        if not reviews:
            raise ObjectDoesNotExistExeption
        return reviews['reviews']

    async def get_movie_review(self, movie_id: str, review_id: str) -> Review:
        filters = {'_id': movie_id, 'reviews.review_id': review_id}
        projection = {'reviews.$': 1}
        review = await self.collection.get_by_id(filters, projection)
        if not review:
            raise ObjectDoesNotExistExeption
        return review['reviews'][0]


def get_reviews_service(
    collection: MongoStorage = Depends(get_film_storage),
) -> ReviewService:
    return ReviewService(collection=collection)
