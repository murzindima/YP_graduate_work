import logging
from contextlib import asynccontextmanager

import uvicorn
from elasticsearch import AsyncElasticsearch, BadRequestError
from pydantic import ValidationError
from redis.asyncio import Redis
from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse

from api.v1 import films, genres, persons
from core import config
from core.logger import LOGGING
from db import elastic, redis
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis.redis = Redis(**dict(config.redis_settings))
    elastic.es = AsyncElasticsearch(hosts=[dict(config.elasticsearch_settings)])
    yield
    await redis.redis.close()
    await elastic.es.close()


app = FastAPI(
    title=config.app_settings.project_name,
    description="A cinema API containing information about movies, genres, and persons.",
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)

app.include_router(films.router, prefix="/api/v1/films", tags=["films"])
app.include_router(genres.router, prefix="/api/v1/genres", tags=["genres"])
app.include_router(persons.router, prefix="/api/v1/persons", tags=["persons"])


@app.exception_handler(ValidationError)
async def handler_validation_error(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content={"errors": exc.errors()}
    )


@app.exception_handler(BadRequestError)
async def handler_bad_request_error(request: Request, exc: BadRequestError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content={"errors": "Bad Request"}
    )


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        log_config=LOGGING,
        log_level=logging.DEBUG,
    )
