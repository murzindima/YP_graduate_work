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
    project_name: str = Field(default="movies")
    # Настройки Redis
    movies_redis_host: str = Field(default="127.0.0.1")
    movies_redis_port: int = Field(default=6379)
    cache_expire_in_seconds: int = 60 * 5  # 5 минут
    # Настройки Elasticsearch
    movies_es_host: str = Field(default="127.0.0.1")
    movies_es_port: int = Field(default=9200)
    standart_page_size: int = 50
    description: str = (
        "Информация о фильмах, жанрах и людях, участвовавших в создании"
        "кинопроизведения"
    )
    version: str = "0.1.0"
    openapi_docs_url: str = "/api/openapi"
    openapi_url: str = "/api/openapi.json"
    access_token_secret_key: str = Field(default="ACCESS_TOKEN_SECRET_KEY")
    token_jwt_algorithm: str = Field(default="HS256")


settings = Settings()
