import logging
from contextlib import asynccontextmanager

import uvicorn
from async_fastapi_jwt_auth import AuthJWT
from async_fastapi_jwt_auth.exceptions import AuthJWTException
from fastapi import Depends, FastAPI
from fastapi.responses import ORJSONResponse
from pydantic import ValidationError
from redis.asyncio import Redis

from src.api.v1 import auth, permissions, roles, users
from src.core.config import app_settings, redis_settings
from src.core.logger import LOGGING
from src.db import redis
from src.exceptions.handlers import authjwt_exception_handler, validation_error_handler
from src.middleware.access_jwt import get_current_user, set_current_user


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis.redis = Redis(**dict(redis_settings), decode_responses=True)
    yield
    await redis.redis.close()


@AuthJWT.load_config
def get_config():
    return app_settings


@AuthJWT.token_in_denylist_loader
async def check_if_token_in_denylist(decrypted_token):
    jti = decrypted_token["jti"]
    entry = await redis.redis.get(jti)
    return entry and entry == "true"


app = FastAPI(
    title=app_settings.project_name,
    description="A service providing authentication methods.",
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(
    users.router,
    prefix="/api/v1/users",
    tags=["users"],
    dependencies=[Depends(set_current_user), Depends(get_current_user)],
)
app.include_router(
    permissions.router,
    prefix="/api/v1/permissions",
    tags=["permissions"],
    dependencies=[Depends(set_current_user), Depends(get_current_user)],
)
app.include_router(
    roles.router,
    prefix="/api/v1/roles",
    tags=["roles"],
    dependencies=[Depends(set_current_user), Depends(get_current_user)],
)

app.exception_handler(AuthJWTException)(authjwt_exception_handler)
app.exception_handler(ValidationError)(validation_error_handler)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        log_config=LOGGING,
        log_level=logging.DEBUG,
    )
