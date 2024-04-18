from fastapi import APIRouter, Depends, Query

from models.films import MovieCreate, MovieInDb
from services.films import FilmService, get_film_service

router = APIRouter()


@router.post('', response_model=MovieInDb, summary='Добавление фильма')
async def create_movie(
    film_data: MovieCreate,
    film_service: FilmService = Depends(get_film_service),
):
    result = await film_service.create_movie(film_data)
    return result


@router.get('/{movie_id}', response_model=MovieInDb, summary='Получение фильма')
async def get_movie(
    movie_id: str, film_service: FilmService = Depends(get_film_service)
):
    movie = await film_service.get_movie(movie_id)
    return movie


@router.delete('/{movie_id}', summary='Удаление фильма')
async def delete_movie(
    movie_id: str, film_service: FilmService = Depends(get_film_service)
):
    return await film_service.delete_movie(movie_id)


@router.get('', response_model=list[MovieInDb], summary='Получение фильмов')
async def get_movies(
    film_service: FilmService = Depends(get_film_service),
        sort_order: str = Query(None, description="Направление сортировки (asc/desc)")):

    result = await film_service.get_movies()

    filtered_items = [MovieInDb.model_validate(item) for item in result]

    if sort_order == "asc":
        filtered_items = sorted(filtered_items, key=lambda x: x.average_rating)
    elif sort_order == "desc":
        filtered_items = sorted(filtered_items, key=lambda x: x.average_rating, reverse=True)

    return filtered_items
