from contextlib import asynccontextmanager

from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient

from api import recommendations
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

app.include_router(
    recommendations.router,
    prefix="/api/v1/recommendations",
    tags=["Рекомендации"],
)
