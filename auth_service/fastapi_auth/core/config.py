import os
from enum import Enum

from authlib.integrations.starlette_client import OAuth
from pydantic import Field, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

# Корень проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(os.path.dirname(BASE_DIR), ".env")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_PATH, env_file_encoding="utf-8", extra="ignore"
    )
    # Настройки подключения к БД
    scheme: str = "postgresql+asyncpg"
    postgres_db: str = Field(default="auth_database")
    postgres_user: str = Field(default="app")
    postgres_password: str = Field(default="123qwe")
    postgres_host: str = Field(default="127.0.0.1")
    postgres_port: int = Field(default=4432)
    # Настройки Redis
    auth_redis_host: str = Field(default="127.0.0.1")
    auth_redis_port: int = Field(default=5379)
    cache_expire_in_seconds: int = 60 * 5  # 5 минут
    # Настройки Fastapi
    auth_fastapi_host: str = Field(default="127.0.0.1")
    auth_fastapi_port: int = Field(default=7005)
    # Настройки Swagger-документации
    project_name: str = Field(default="auth-service")
    version: str = "0.1.0"
    description: str = "Пользователи сервиса"
    openapi_docs_url: str = "/auth/openapi"
    openapi_url: str = "/auth/openapi.json"
    prefix: str = "/auth/v1"

    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 10
    access_token_secret_key: str = Field(default="ACCESS_TOKEN_SECRET_KEY")
    refresh_token_secret_key: str = Field(default="REFRESH_TOKEN_SECRET_KEY")
    token_jwt_algorithm: str = "HS256"

    min_username_length: int = 1
    max_username_length: int = 255
    username_pattern: str = (
        f"^[a-zA-Z0-9_-]{{{min_username_length},{max_username_length}}}$"
    )
    max_email_length: int = 255
    max_password_length: int = 255
    max_first_name_length: int = 50
    max_last_name_length: int = 50

    max_role_title_length: int = 255
    max_role_description_length: int = 255

    # минимальный и максимальный размер нешифрованного пароля
    min_password_input_length: int = 4
    max_password_input_length: int = 60

    standart_page_size: int = 10

    request_limit_per_minute: int = 20

    # Настройки Yandex
    yandex_token_url: str = "https://oauth.yandex.ru/"
    yandex_url: str = "https://oauth.yandex.ru/authorize?response_type=code"
    yandex_login_url: str = "https://login.yandex.ru/info?format=json"
    yandex_client_id: str = Field(default="YANDEX_CLIENT_ID")
    yandex_client_secret: str = Field(default="YANDEX_CLIENT_SECRET")

    session_cookie: str = "your_session_cookie"

    # Настройки Jaeger
    jaeger_host: str = Field(default="jaeger-auth")
    jaeger_port: int = Field(default=6831)
    enable_tracer: bool = Field(default=True)

    @property
    def dsn(self) -> PostgresDsn:
        return str(
            PostgresDsn.build(
                scheme=self.scheme,
                username=self.postgres_user,
                password=self.postgres_password,
                host=self.postgres_host,
                port=self.postgres_port,
                path=self.postgres_db,
            )
        )


settings = Settings()


class RightsName(str, Enum):
    """Модель прав доступа в API."""

    admin = "admin"


class SocialNetworks(str, Enum):
    """Социальные сети для авторизации."""

    yandex = "yandex"
    google = "google"


class SettingsYandexOauth(BaseSettings):
    name: str = SocialNetworks.yandex
    authorize_url: str = settings.yandex_url
    access_token_url: str = settings.yandex_token_url
    api_base_url: str = settings.yandex_login_url
    client_id: str = settings.yandex_client_id
    client_secret: str = settings.yandex_client_secret


oauth = OAuth()
oauth.register(**dict(SettingsYandexOauth()))
