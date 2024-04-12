from fastapi import APIRouter, Depends

from models.films import Review, ReviewCreate
from models.user import User
from services.reviews import ReviewService, get_reviews_service
from services.token import get_user

router = APIRouter()


@router.post('/{movie_id}', summary='Добавление отзыва на фильм')
async def review_film(
    review: ReviewCreate,
    movie_id: str,
    review_service: ReviewService = Depends(get_reviews_service),
    user: User = Depends(get_user()),
):
    result = await review_service.add_review(movie_id, user.user_id, review)
    return result


@router.delete('/{movie_id}/{review_id}', summary='Удаление отзыва')
async def delete_like_film(
    movie_id: str,
    review_id: str,
    review_service: ReviewService = Depends(get_reviews_service),
):
    result = await review_service.remove_review_from_movie(movie_id, review_id)
    return result


@router.get(
    '/{movie_id}',
    response_model=list[Review],
    summary='Получение отзывов фильма',
)
async def get_movie_reviews(
    movie_id: str, review_service: ReviewService = Depends(get_reviews_service),
):
    result = await review_service.get_movie_reviews(movie_id)
    return result


@router.get(
    '/{movie_id}/{review_id}',
    response_model=Review,
    summary='Получение конкретного отзыва',
)
async def get_movie_review(
    movie_id: str,
    review_id: str,
    review_service: ReviewService = Depends(get_reviews_service),
):
    result = await review_service.get_movie_review(movie_id, review_id)
    return result
