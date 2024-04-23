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

    recommendations_endpoint: str = Field(default="/api/v1/recommendations/create_matrices")
    recommendations_host: str = Field(default="localhost")
    recommendations_port: str = Field(default="80")

    cron_logfile: str = Field(default="/usr/src/cron/logs/cron.log")


settings = Settings()
