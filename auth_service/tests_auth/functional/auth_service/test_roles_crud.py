from http import HTTPStatus
from typing import Callable

import orjson

from functional.settings import test_settings


ROLE_DATA = {
    "title": "role_1",
    "description": "about role_1",
}


async def test_create_role(
    make_post_request: Callable,
    admin_headers: dict,
):
    """Проверка создания новой роли."""

    response = await make_post_request(
        endpoint=test_settings.common_roles,
        data=orjson.dumps(ROLE_DATA),
        headers=admin_headers,
    )
    data = response["body"]

    assert response["status"] == HTTPStatus.CREATED
    assert data["title"] == ROLE_DATA["title"]
    assert data["description"] == ROLE_DATA["description"]


async def test_create_role_unique(
    make_post_request: Callable,
    admin_headers: dict,
):
    """Проверка невозможности создания новой роли с тем же именем."""

    response = {}
    for _ in range(2):
        response = await make_post_request(
            endpoint=test_settings.common_roles,
            data=orjson.dumps(ROLE_DATA),
            headers=admin_headers,
        )
    data = response["body"]

    assert response["status"] == HTTPStatus.BAD_REQUEST
    assert data["detail"] == "Такая роль уже существует."


async def test_get_role_by_title(
    role_in_db: Callable,
    make_get_request: Callable,
    admin_headers: dict,
):
    """Проверка получения роли по названию."""

    role_title = "role_1"

    response = await make_get_request(
        endpoint=f"{test_settings.common_roles}/{role_title}",
        headers=admin_headers,
    )
    data = response["body"]

    assert response["status"] == HTTPStatus.OK
    assert data["title"] == ROLE_DATA["title"]
    assert data["description"] == ROLE_DATA["description"]


async def test_update_role(
    role_in_db: Callable, make_patch_request: Callable, admin_headers: dict
):
    """Проверка возможности изменения роли."""

    role_title = "role_1"
    new_role_data = {
        "title": "role_2",
        "description": "about role_2",
    }
    response = await make_patch_request(
        endpoint=f"{test_settings.common_roles}/{role_title}",
        data=orjson.dumps(new_role_data),
        headers=admin_headers,
    )
    data = response["body"]

    assert response["status"] == HTTPStatus.OK
    assert data["title"] == new_role_data["title"]
    assert data["description"] == new_role_data["description"]


async def test_delete_role(
    role_in_db: Callable,
    make_delete_request: Callable,
    is_id_exists: Callable,
    admin_headers: dict,
):
    """Проверка возможности удаления роли."""

    role_title = "role_1"
    role_id = "11111111-1111-1111-1111-111111111111"

    response = await make_delete_request(
        endpoint=f"{test_settings.common_roles}/{role_title}",
        headers=admin_headers,
    )
    result = await is_id_exists("role", role_id)

    assert not result
    assert response["status"] == HTTPStatus.OK
