from pydantic import Field, HttpUrl, RedisDsn, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class TestSettings(BaseSettings):
    model_config = SettingsConfigDict()

    project_name: str = Field(default="test_auth")

    auth_test_redis_host: str = Field(default="127.0.0.1")
    auth_test_redis_port: int = Field(default=5380)

    auth_test_fastapi_host: str = Field(default="127.0.0.1")
    auth_test_fastapi_port: int = Field(default=7001)

    auth_test_postgres_host: str = Field(default="127.0.0.1")
    auth_test_postgres_port: int = Field(default=4433)
    auth_test_postgres_db: str = Field(default="auth_database")
    auth_test_postgres_user: str = Field(default="app")
    auth_test_postgres_password: str = Field(default="123qwe")

    @property
    def app_url(self) -> HttpUrl:
        return (
            f"http://{self.auth_test_fastapi_host}:"
            f"{self.auth_test_fastapi_port}"
        )

    @property
    def redis_dsn(self) -> RedisDsn:
        return (
            f"redis://{self.auth_test_redis_host}:{self.auth_test_redis_port}"
        )

    @property
    def postgres_dsn(self) -> PostgresDsn:
        return (
            f"postgresql://{self.auth_test_postgres_user}:{self.auth_test_postgres_password}@"
            f"{self.auth_test_postgres_host}:{self.auth_test_postgres_port}/"
            f"{self.auth_test_postgres_db}"
        )

    # Настройки суперпользователя
    superuser_name: str = Field(default="admin")
    superuser_email: str = Field(default="admin@admin.com")
    superuser_password: str = Field(default="password")
    superuser_first_name: str = Field(default="first_name")
    superuser_last_name: str = Field(default="last_name")

    #  endpoint paths
    common_users: str = "/auth/v1/users"
    endpoint_sign_up: str = "/signup"
    endpoint_me: str = "/me"
    endpoint_history: str = "/history"
    endpoint_roles: str = "/roles"

    common_roles: str = "/auth/v1/roles"

    common_auth: str = "/auth/v1/auth"
    endpoint_login: str = "/login"
    endpoint_refresh: str = "/refresh"

    headers_login: dict = {"Content-type": "application/x-www-form-urlencoded"}
    headers_common: dict = {"Content-Type": "application/json"}

    access_token_secret_key: str = Field(default="ACCESS_TOKEN_SECRET_KEY")
    refresh_token_secret_key: str = Field(default="REFRESH_TOKEN_SECRET_KEY")
    token_jwt_algorithm: str = "HS256"


test_settings = TestSettings()
