from fastapi import APIRouter, Depends

from models.favourites import Favourite, UserInDb
from models.user import User
from services.favourites import FavouritesService, get_favourites_service
from services.token import get_user

router = APIRouter()


@router.post(
    '', response_model=Favourite, summary='Добавление закладки фильму'
)
async def add_like_film(
    favourite: Favourite,
    user: User = Depends(get_user()),
    favourites_service: FavouritesService = Depends(get_favourites_service),
):
    result = await favourites_service.create_favourite(favourite, user.user_id)
    return result


@router.delete('/{film_id}', summary='Удаление закладки у фильма')
async def remove_favourite_film(
    film_id: str,
    favourites_service: FavouritesService = Depends(get_favourites_service),
    user: User = Depends(get_user()),
):
    result = await favourites_service.delete_favourite(film_id, user.user_id)
    return result


@router.post(
    '/{user_id}',
    response_model=UserInDb,
    summary='Список закладок пользователя',
)
async def get_user_favourites(
    favourites_service: FavouritesService = Depends(get_favourites_service),
    user: User = Depends(get_user()),
):
    result = await favourites_service.get_user_favourites(user.user_id)
    return result


@router.get(
    '',
    response_model=list[UserInDb],
    summary='Список пользователей',
)
async def get_all_favourites(
    favourites_service: FavouritesService = Depends(get_favourites_service),
):
    result = await favourites_service.get_all_favourites()
    return result
