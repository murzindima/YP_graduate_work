from typing import Callable
import orjson
import pytest

from functional.settings import test_settings


@pytest.fixture
def create_user_role(make_post_request: Callable) -> Callable:
    """Добавить пользователю роль от имени user."""

    async def inner(
        user_role_data: dict,
        headers: dict | None = test_settings.headers_common,
    ) -> dict:
        username = user_role_data["username"]
        endpoint_role_to_user = f"{test_settings.common_users}/{username}{test_settings.endpoint_roles}"
        response = await make_post_request(
            headers=headers,
            data=orjson.dumps(user_role_data),
            endpoint=endpoint_role_to_user,
        )
        return response

    return inner


@pytest.fixture
def remove_user_role(make_delete_request: Callable) -> Callable:
    """Удалить у пользователя роль от имени user."""

    async def inner(
        user_role_data: dict,
        headers: dict | None = test_settings.headers_common,
    ) -> dict:
        username = user_role_data["username"]
        endpoint_role_to_user = f"{test_settings.common_users}/{username}{test_settings.endpoint_roles}"
        response = await make_delete_request(
            headers=headers,
            data=orjson.dumps(user_role_data),
            endpoint=endpoint_role_to_user,
        )
        return response

    return inner
