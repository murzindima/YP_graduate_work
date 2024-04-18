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
    project_name: str = Field(default="Recommendations")
    description: str = "Сервис рекомендаций пользователям"
    version: str = "0.1.0"
    openapi_docs_url: str = "/api/openapi"
    openapi_url: str = "/api/openapi.json"
    access_token_secret_key: str = Field(default="ACCESS_TOKEN_SECRET_KEY")
    token_jwt_algorithm: str = Field(default="HS256")
    mongo_recommendations_host: str = Field(default="localhost")
    mongo_recommendations_port: int = Field(default=27018)
    mongo_db_name: str = Field(default="movie_recommender")

    num_recommendations: int = 5
    num_similar_users: int = 5
    ugc_movies_endpoint: str = Field(default="localhost:80/api/v1/movies")
    new_movies_endpoint: str = Field(default="localhost:80/api/v1/movies")
    best_ugc_endpoint: str = Field(default="localhost:80/api/v1/ugc")

    new_recommendation_endpoint: str = Field(default="localhost:80/api/v1/recommendations/update_new")
    best_recommendation_endpoint: str = Field(default="localhost:80/api/v1/recommendations/update_best")
    similar_recommendation_endpoint: str = Field(default="localhost:80/api/v1/recommendations/create_matrices")

    api_new: str = ""
    api_best: str = ""
    api_similar: str = ""

    @property
    def mongo_dsn(self) -> str:
        return f"{self.mongo_recommendations_host}:{self.mongo_recommendations_port}"


settings = Settings()
