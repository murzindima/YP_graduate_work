from uuid import UUID

from pydantic import BaseModel, ConfigDict


class SocialAccountUserId(BaseModel):
    user_id: UUID

    model_config = ConfigDict(from_attributes=True)


class SocialAccountInDB(SocialAccountUserId):
    social_id: str
    social_name: str
