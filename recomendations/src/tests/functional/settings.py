from pydantic_settings import BaseSettings


class TestSettings(BaseSettings):
    auth_api_url: str = "http://auth-api:80/api/v1"
    notifications_api_url: str = "http://notifications-api:80/api/v1"


test_settings = TestSettings()
