from typing import Callable

import pytest
import json

from jose import jwt

from functional.settings import test_settings
from functional.test_data.roles_data import admin


ENDPOINT_LOGIN = f"{test_settings.common_auth}{test_settings.endpoint_login}"
ENDPOINT_REFRESH = (
    f"{test_settings.common_auth}{test_settings.endpoint_refresh}"
)


@pytest.fixture
def login_user(
    make_post_request: Callable,
) -> Callable:
    """Получение headers c токеном пользователя."""

    async def inner(
        user: dict | None = None,
    ):
        response = await make_post_request(
            headers=test_settings.headers_login,
            endpoint=ENDPOINT_LOGIN,
            data=user,
        )

        return response

    return inner


@pytest.fixture
def get_authorization_headers(
    make_post_request: Callable,
) -> Callable:
    """Получение headers c токеном пользователя."""

    async def inner(
        user: dict | None = None,
    ) -> dict:
        response = await make_post_request(
            headers=test_settings.headers_login,
            endpoint=ENDPOINT_LOGIN,
            data=user,
        )
        access_token = response["body"]["access_token"]
        tokens_type = response["body"]["tokens_type"]
        authorization_headers = {
            "Authorization": f"{tokens_type} {access_token}"
        }
        headers = authorization_headers | test_settings.headers_common
        return headers

    return inner


@pytest.fixture
def get_tokens(
    make_post_request: Callable,
) -> Callable:
    """Получение токенов пользователя."""

    async def inner(
        user: dict | None = None,
    ) -> dict:
        response = await make_post_request(
            headers=test_settings.headers_login,
            endpoint=ENDPOINT_LOGIN,
            data=user,
        )
        return response

    return inner


@pytest.fixture
def read_token() -> Callable:
    """Чтение содержимого токенов пользователя."""

    def inner(secret_key: str, token: str) -> dict:
        payload = jwt.decode(
            token,
            secret_key,
            algorithms=test_settings.token_jwt_algorithm,
        )
        username = payload.get("username")
        roles = payload.get("roles")
        user_id = payload.get("user_id")
        exp = payload.get("exp")
        data = {
            "username": username,
            "roles": roles,
            "user_id": user_id,
            "exp": exp,
        }
        return data

    return inner


@pytest.fixture
def refresh_token(make_post_request: Callable) -> Callable:
    """Получение токенов по refresh токену пользователя."""

    async def inner(
        refresh_token_str: str | None = None,
    ) -> dict:
        response = await make_post_request(
            headers=test_settings.headers_common,
            endpoint=ENDPOINT_REFRESH,
            data=json.dumps({"token": refresh_token_str}),
        )
        return response

    return inner


@pytest.fixture
async def admin_headers(get_authorization_headers) -> dict[str, str]:
    """Headers для авторизованного админа"""
    admin_headers = await get_authorization_headers(admin)
    return admin_headers
