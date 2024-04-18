from typing_extensions import Annotated

import bcrypt
from pydantic import BaseModel, Field


class PageParams(BaseModel):
    limit: Annotated[int, Field(ge=1)] | None = None
    offset: Annotated[int, Field(ge=0)] = 0


def create_hash(string: str) -> str:
    """Делает из строки ХЭШ."""
    hashed_string_b: bytes = bcrypt.hashpw(
        string.encode("utf-8"), bcrypt.gensalt()
    )
    hashed_string: str = hashed_string_b.decode("utf-8")
    return hashed_string


def check_password(password: str, hashed_password: str) -> bool:
    result = bool(
        bcrypt.checkpw(
            password.encode("utf-8"), hashed_password.encode("utf-8")
        )
    )
    return result
