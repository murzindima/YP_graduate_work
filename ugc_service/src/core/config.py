import os

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Корень проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(os.path.dirname(BASE_DIR), ".env")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_PATH, env_file_encoding="utf-8", extra="ignore"
    )
    # Название проекта. Используется в Swagger-документации
    project_name: str = Field(default="ugc")
    description: str = "Информация о отзвах, лайках, закладках пользователей"
    version: str = "0.1.0"
    openapi_docs_url: str = "/api/openapi"
    openapi_url: str = "/api/openapi.json"
    access_token_secret_key: str = Field(default="ACCESS_TOKEN_SECRET_KEY")
    token_jwt_algorithm: str = Field(default="HS256")
    mongo_host: str = Field(default="localhost")
    mongo_port: int = Field(default=27017)
    mongo_db_name: str = Field(default="ugc")

    @property
    def mongo_dsn(self) -> str:
        return f"{self.mongo_host}:{self.mongo_port}"


settings = Settings()
