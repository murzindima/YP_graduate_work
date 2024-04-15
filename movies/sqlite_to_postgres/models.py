"""Модели датаклассов для таблиц."""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID


@dataclass
class IDCreatedMixin:
    """Абстрактная модель для полей ID и created_at."""

    id: UUID
    created_at: datetime

    class Meta:
        abstract = True


@dataclass
class UpdatedMixin:
    """Абстрактная модель для поля updated_at."""

    updated_at: datetime


@dataclass
class Genre(IDCreatedMixin, UpdatedMixin):
    name: str
    description: str


@dataclass
class GenreFilmWork(IDCreatedMixin):
    film_work_id: UUID
    genre_id: UUID


@dataclass
class PersonFilmWork(IDCreatedMixin):
    film_work_id: UUID
    person_id: UUID
    role: str


@dataclass
class Person(IDCreatedMixin, UpdatedMixin):
    full_name: str


@dataclass
class FilmWork(IDCreatedMixin, UpdatedMixin):
    title: str
    description: str
    creation_date: datetime
    rating: float
    type: str = field(default="movie")
