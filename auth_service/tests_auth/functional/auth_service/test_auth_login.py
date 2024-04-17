from http import HTTPStatus
from typing import Callable

from functional.test_data.roles_data import admin, user


async def test_correct_login(
    login_user: Callable,
) -> None:
    """Добавляем пользователя и получаем токены."""
    response = await login_user(admin)

    assert response["status"] == HTTPStatus.OK


async def test_login_without_user_in_bd(
    login_user: Callable,
) -> None:
    """Получаем токены на несуществующего пользователя."""
    response = await login_user(user)

    assert response["status"] == HTTPStatus.NOT_FOUND
