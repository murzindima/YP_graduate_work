from pydantic import BaseModel, Field, validator


class BaseInMongo(BaseModel):
    id: str | None = Field(alias='_id')

    @validator('id', pre=True, always=True)
    @classmethod
    def convert_to_str(cls, _id: str) -> str | None:
        if _id:
            return str(_id)
        return None
