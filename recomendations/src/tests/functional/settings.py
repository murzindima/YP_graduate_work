from pydantic_settings import BaseSettings


class TestSettings(BaseSettings):
    recommendations_api_base_url: str = "http://host.docker.internal:90/api/v1/recommendations"


test_settings = TestSettings()
