from contextlib import asynccontextmanager

from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient

from api import favourites, likes, movies, reviews
from core.config import settings
from db import mongo


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Определение логики работы (запуска и остановки) приложения."""
    # Логика при запуске приложения.
    mongo.mongodb = AsyncIOMotorClient(settings.mongo_dsn)
    yield
    # Логика при завершении приложения.
    mongo.mongodb.close()


app = FastAPI(
    lifespan=lifespan,
    title=settings.project_name,
    description=settings.description,
    version=settings.version,
    docs_url=settings.openapi_docs_url,
    openapi_url=settings.openapi_url,
)

app.include_router(movies.router, prefix='/api/v1/movies', tags=['Фильмы'])
app.include_router(likes.router, prefix='/api/v1/likes', tags=['Лайки'])
app.include_router(
    favourites.router, prefix='/api/v1/favourites', tags=['Закладки']
)
app.include_router(reviews.router, prefix='/api/v1/reviews', tags=['Отзывы'])
