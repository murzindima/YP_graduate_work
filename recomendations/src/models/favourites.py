from pydantic import BaseModel

from core.models import BaseInMongo


class Favourite(BaseModel):
    film_id: str


class UserInDb(BaseInMongo):
    user_id: str
    favourites: list[Favourite] | None
