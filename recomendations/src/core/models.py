from pydantic import BaseModel, Field, validator
from pymongo.collection import ObjectId


class BaseInMongo(BaseModel):
    id: str | None = Field(alias='_id')

    @validator('id', pre=True, always=True)
    @classmethod
    def convert_to_str(cls, _id: ObjectId) -> str | None:
        if _id:
            return str(_id)
        return None