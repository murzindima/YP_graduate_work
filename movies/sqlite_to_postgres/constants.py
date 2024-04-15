"""Константы для перекачки БД."""
import os

from dotenv import load_dotenv

from models import (
    FilmWork,
    Genre,
    GenreFilmWork,
    Person,
    PersonFilmWork,
)

load_dotenv()

TABLES_TO_CLASSES = {
    "film_work": FilmWork,
    "genre": Genre,
    "person": Person,
    "genre_film_work": GenreFilmWork,
    "person_film_work": PersonFilmWork,
}

UPLOAD_SIZE = 20

COLUMN_NAME_CORRESPONDENCE = {
    "id": "id",
    "name": "name",
    "description": "description",
    "full_name": "full_name",
    "title": "title",
    "creation_date": "creation_date",
    "type": "type",
    "rating": "rating",
    "genres": "genres",
    "persons": "persons",
    "film_work": "film_work",
    "person": "person",
    "role": "role",
    "genre": "genre",
    "created_at": "created",
    "updated_at": "modified",
    "film_work_id": "film_work_id",
    "genre_id": "genre_id",
    "person_id": "person_id",
}

DSL = {
    "dbname": os.environ.get("DB_NAME", "movies_database"),
    "user": os.environ.get("DB_USER", "app"),
    "password": os.environ.get("DB_PASSWORD", "123qwe"),
    "host": os.environ.get("DB_HOST", "127.0.0.1"),
    "port": os.environ.get("DB_PORT", "5432"),
    "options": "-c search_path=content",
}

RESOURSE_DB = os.environ.get("RESOURCE_DB", "db.sqlite")
