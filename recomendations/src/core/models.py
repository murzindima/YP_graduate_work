from uuid import UUID

from pydantic import BaseModel


class FilmShort(BaseModel):
    """Короткая модель ответа API по кинопроизведениям."""

    uuid: UUID
    title: str | None = ""
    imdb_rating: float | None = 0
