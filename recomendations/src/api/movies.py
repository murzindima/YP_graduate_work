from fastapi import APIRouter, Depends

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
async def get_movies(film_service: FilmService = Depends(get_film_service)):
    result = await film_service.get_movies()
    return result
