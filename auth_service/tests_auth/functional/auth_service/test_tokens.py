"""Проверка добавления ролей пользователю."""
import time
from datetime import datetime
from http import HTTPStatus
from typing import Callable

from functional.settings import test_settings
from functional.test_data.roles_data import (
    roles,
    admin,
    user,
    no_user,
    role_to_admin,
)


async def test_get_tokens_without_user_in_db(
    get_tokens: Callable,
) -> None:
    """Получаем токены на незарегистрированного пользователя"""
    response = await get_tokens(user)
    assert response["status"] == HTTPStatus.NOT_FOUND
    assert response["body"] == no_user


async def test_tokens_have_all_atributes(
    get_tokens: Callable,
    read_token: Callable,
) -> None:
    """Проверяем целостность состава токенов."""
    token = await get_tokens(admin)
    token_data = token["body"]
    assert token_data["tokens_type"] == "bearer"
    access_token = token_data["access_token"]
    refresh_token = token_data["refresh_token"]
    access_token_data = read_token(
        secret_key=test_settings.access_token_secret_key, token=access_token
    )
    refresh_token_data = read_token(
        secret_key=test_settings.refresh_token_secret_key, token=refresh_token
    )
    assert access_token_data["username"] == admin["username"]
    assert access_token_data["user_id"] == admin["id"]
    assert access_token_data["roles"] == ["admin"]
    assert access_token_data["exp"] > int(datetime.utcnow().timestamp())
    assert access_token_data["username"] == refresh_token_data["username"]
    assert access_token_data["user_id"] == refresh_token_data["user_id"]
    assert access_token_data["roles"] == refresh_token_data["roles"]
    assert access_token_data["exp"] < refresh_token_data["exp"]


async def test_tokens_have_correct_number_titles_with_two_roles(
    get_tokens: Callable,
    read_token: Callable,
    create_role: Callable,
    get_authorization_headers: Callable,
    create_user_role: Callable,
) -> None:
    """Проверяем назначение двух ролей пользователю отражается в токене."""
    admin_headers = await get_authorization_headers(admin)
    await create_role(headers=admin_headers, role_data=roles[0])
    await create_user_role(
        headers=admin_headers, user_role_data=role_to_admin[0]
    )
    token = await get_tokens(admin)
    token_data = token["body"]
    access_token = token_data["access_token"]
    access_token_data = read_token(
        secret_key=test_settings.access_token_secret_key, token=access_token
    )
    assert role_to_admin[0]["title"] in access_token_data["roles"]
    assert len(access_token_data["roles"]) == 2


async def test_get_tokens_by_correct_refresh_token(
    get_tokens: Callable,
    refresh_token: Callable,
    read_token: Callable,
) -> None:
    """Получаем валидные токены по refresh токену."""
    token = await get_tokens(admin)
    token_data = token["body"]
    refresh_token_str = token_data["refresh_token"]
    time.sleep(1)
    new_tokens = await refresh_token(refresh_token_str)
    new_token_data = new_tokens["body"]
    assert new_tokens["status"] == HTTPStatus.OK
    assert new_token_data["tokens_type"] == "bearer"
    access_token = new_token_data["access_token"]
    refresh_token_str = new_token_data["refresh_token"]
    access_token_data = read_token(
        secret_key=test_settings.access_token_secret_key, token=access_token
    )
    refresh_token_data = read_token(
        secret_key=test_settings.refresh_token_secret_key,
        token=refresh_token_str,
    )
    assert access_token_data["username"] == admin["username"]
    assert access_token_data["user_id"] == admin["id"]
    assert access_token_data["roles"] == ["admin"]
    assert access_token_data["exp"] > int(datetime.utcnow().timestamp())
    assert access_token_data["username"] == refresh_token_data["username"]
    assert access_token_data["user_id"] == refresh_token_data["user_id"]
    assert access_token_data["roles"] == refresh_token_data["roles"]
    assert access_token_data["exp"] < refresh_token_data["exp"]
