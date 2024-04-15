from pydantic import BaseModel, EmailStr


class User(BaseModel):
    user_id: str
    username: str
    roles: list
    email: EmailStr
    first_name: str
    last_name: str
