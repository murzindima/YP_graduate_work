from pydantic import BaseModel, computed_field

from core.models import BaseInMongo


class Like(BaseModel):
    user_id: str
    rating: int


class LikeCreate(BaseModel):
    rating: int


class Review(BaseModel):
    review_id: str
    user_id: str
    article: str
    text: str
    likes: list[Like] = []

    @computed_field
    def average_rating(self) -> float:
        if not self.likes:
            return 0
        return sum(like.rating for like in self.likes) / len(self.likes)


class ReviewCreate(BaseModel):
    article: str
    text: str


class MovieInDb(BaseInMongo):
    title: str
    reviews: list[Review] | None
    likes: list[Like] | None

    @computed_field
    def average_rating(self) -> float:
        if not self.likes:
            return 0
        return sum(like.rating for like in self.likes) / len(self.likes)


class MovieCreate(BaseModel):
    id: str
    title: str
    reviews: list[Review] | None
    likes: list[Like] | None
