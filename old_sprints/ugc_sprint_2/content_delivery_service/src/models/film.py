from models.base import UUIDMixIn
from models.genre import Genre
from models.person import Person


class Film(UUIDMixIn):
    """
    Pydantic model representing a film.

    Attributes:
    - uuid (uuid.UUID): The universally unique identifier of the film.
    - title (str): The title of the film.
    - description (str): A description of the film.
    - imdb_rating (float | None): The IMDb rating of the film, if available. Can be None.
    - genres (List[Genre]): A list of Genre objects representing the genres associated with the film.
    - directors (List[Person]): A list of Person objects representing the directors of the film.
    - actors (List[Person]): A list of Person objects representing the actors in the film.
    - writers (List[Person]): A list of Person objects representing the writers of the film.
    """

    title: str
    description: str
    imdb_rating: float | None
    genres: list[Genre]
    directors: list[Person]
    actors: list[Person]
    writers: list[Person]
