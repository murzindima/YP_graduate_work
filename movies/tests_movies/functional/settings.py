from enum import Enum
from typing import Any

from pydantic import Field, HttpUrl, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class IndexName(str, Enum):
    GENRES = "genres"
    MOVIES = "movies"
    PERSONS = "persons"

    def __str__(self) -> str:
        return str.__str__(self)


class IndexSettings(BaseSettings):
    model_config = SettingsConfigDict(use_enum_values=True)

    SETTINGS: dict[str, Any] = {
        "refresh_interval": "1s",
        "analysis": {
            "filter": {
                "english_stop": {"type": "stop", "stopwords": "_english_"},
                "english_stemmer": {"type": "stemmer", "language": "english"},
                "english_possessive_stemmer": {
                    "type": "stemmer",
                    "language": "possessive_english",
                },
                "russian_stop": {"type": "stop", "stopwords": "_russian_"},
                "russian_stemmer": {"type": "stemmer", "language": "russian"},
            },
            "analyzer": {
                "ru_en": {
                    "tokenizer": "standard",
                    "filter": [
                        "lowercase",
                        "english_stop",
                        "english_stemmer",
                        "english_possessive_stemmer",
                        "russian_stop",
                        "russian_stemmer",
                    ],
                }
            },
        },
    }
    MAPPINGS: dict[IndexName, Any] = {
        IndexName.GENRES: {
            "dynamic": "strict",
            "properties": {
                "uuid": {"type": "keyword"},
                "name": {"type": "keyword"},
                "description": {"type": "text", "analyzer": "ru_en"},
            },
        },
        IndexName.MOVIES: {
            "dynamic": "strict",
            "properties": {
                "uuid": {"type": "keyword"},
                "imdb_rating": {"type": "float"},
                "genre": {
                    "type": "nested",
                    "dynamic": "strict",
                    "properties": {
                        "uuid": {"type": "keyword"},
                        "name": {"type": "text", "analyzer": "ru_en"},
                    },
                },
                "title": {
                    "type": "text",
                    "analyzer": "ru_en",
                    "fields": {"raw": {"type": "keyword"}},
                },
                "description": {"type": "text", "analyzer": "ru_en"},
                "actors": {
                    "type": "nested",
                    "dynamic": "strict",
                    "properties": {
                        "uuid": {"type": "keyword"},
                        "full_name": {"type": "text", "analyzer": "ru_en"},
                    },
                },
                "writers": {
                    "type": "nested",
                    "dynamic": "strict",
                    "properties": {
                        "uuid": {"type": "keyword"},
                        "full_name": {"type": "text", "analyzer": "ru_en"},
                    },
                },
                "directors": {
                    "type": "nested",
                    "dynamic": "strict",
                    "properties": {
                        "uuid": {"type": "keyword"},
                        "full_name": {"type": "text", "analyzer": "ru_en"},
                    },
                },
            },
        },
        IndexName.PERSONS: {
            "dynamic": "strict",
            "properties": {
                "uuid": {"type": "keyword"},
                "full_name": {
                    "type": "text",
                    "analyzer": "ru_en",
                    "fields": {"raw": {"type": "keyword"}},
                },
                "films": {
                    "type": "nested",
                    "dynamic": "strict",
                    "properties": {
                        "uuid": {"type": "keyword"},
                        "imdb_rating": {"type": "float"},
                        "title": {"type": "text", "analyzer": "ru_en"},
                        "roles": {"type": "text", "analyzer": "ru_en"},
                    },
                },
            },
        },
    }


class TestSettings(BaseSettings):
    model_config = SettingsConfigDict()

    PROJECT_NAME: str = Field(default="test_movies")

    MOVIES_TEST_REDIS_HOST: str = Field(default="127.0.0.1")
    MOVIES_REDIS_PORT: int = Field(default=6379)

    MOVIES_TEST_ES_HOST: str = Field(default="127.0.0.1")
    MOVIES_ES_PORT: int = Field(default=9200)

    MOVIES_TEST_FASTAPI_HOST: str = Field(default="127.0.0.1")
    MOVIES_FASTAPI_PORT: int = Field(default=8003)

    headers_common: dict = {"Content-Type": "application/json"}

    access_token_secret_key: str = Field(default="ACCESS_TOKEN_SECRET_KEY")
    token_jwt_algorithm: str = Field(default="HS256")

    @property
    def app_url(self) -> HttpUrl:
        return f"http://{self.MOVIES_TEST_FASTAPI_HOST}:{self.MOVIES_FASTAPI_PORT}"

    @property
    def es_url(self) -> HttpUrl:
        return f"http://{self.MOVIES_TEST_ES_HOST}:{self.MOVIES_ES_PORT}"

    @property
    def redis_dsn(self) -> RedisDsn:
        return (
            f"redis://{self.MOVIES_TEST_REDIS_HOST}:{self.MOVIES_REDIS_PORT}"
        )


test_settings = TestSettings()
index_settings = IndexSettings()
