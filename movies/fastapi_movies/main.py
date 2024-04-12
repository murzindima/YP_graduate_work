from contextlib import asynccontextmanager

from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis

from api.v1 import films, genres, persons
from core.config import settings
from core.logger import logger
from db import elastic, redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Определение логики работы (запуска и остановки) приложения."""
    # Логика при запуске приложения.
    redis.redis = Redis(
        host=settings.movies_redis_host, port=settings.movies_redis_port
    )
    elastic.es = AsyncElasticsearch(
        hosts=[f"{settings.movies_es_host}:{settings.movies_es_port}"]
    )
    logger.info("Приложение запущено")
    yield
    # Логика при завершении приложения.
    await redis.redis.close()
    await elastic.es.close()
    logger.info("Приложение остановлено")


app = FastAPI(
    lifespan=lifespan,
    title=settings.project_name,
    description=settings.description,
    version=settings.version,
    docs_url=settings.openapi_docs_url,
    openapi_url=settings.openapi_url,
    default_response_class=ORJSONResponse,
)

app.include_router(
    films.router, prefix="/api/v1/films", tags=["Кинопроизведения"]
)
app.include_router(persons.router, prefix="/api/v1/persons", tags=["Персоны"])
app.include_router(genres.router, prefix="/api/v1/genres", tags=["Жанры"])
