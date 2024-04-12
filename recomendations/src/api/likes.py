from fastapi import APIRouter, Depends

from models.films import LikeCreate
from models.user import User
from services.like import LikeService, get_like_service
from services.token import get_user

router = APIRouter()


@router.post('/{movie_id}', summary='Добавление лайка фильма')
async def like_film(
    like: LikeCreate,
    movie_id: str,
    user: User = Depends(get_user()),
    like_service: LikeService = Depends(get_like_service),
):
    result = await like_service.like_movie(movie_id, user.user_id, like)
    return result


@router.delete('/{movie_id}', summary='Удаление лайка фильма')
async def delete_like_film(
    movie_id: str,
    user: User = Depends(get_user()),
    like_service: LikeService = Depends(get_like_service),
):
    result = await like_service.remove_like_from_movie(movie_id, user.user_id)
    return result


@router.post('/{movie_id}/{review_id"}', summary='Добавление лайка отзыва')
async def like_review(
    like: LikeCreate,
    movie_id: str,
    review_id: str,
    user: User = Depends(get_user()),
    like_service: LikeService = Depends(get_like_service),
):
    result = await like_service.like_review(
        movie_id, review_id, user.user_id, like
    )
    return result


@router.delete('/{movie_id}/{review_id"}', summary='Удаление лайка отзыва')
async def delete_like_review(
    movie_id: str,
    review_id: str,
    user: User = Depends(get_user()),
    like_service: LikeService = Depends(get_like_service),
):
    result = await like_service.remove_like_from_review(
        movie_id, review_id, user.user_id
    )
    return result
