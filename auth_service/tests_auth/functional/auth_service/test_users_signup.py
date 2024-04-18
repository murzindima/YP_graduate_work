"""Проверка регистрации пользователя при заполнении формы signup"""

from asyncpg import Record
from http import HTTPStatus
from typing import Callable
import pytest
from functional.test_data.users_data import (
    all_incorrect_users,
    correct_user,
    check_user_in_db_sql,
)
from functional.test_data.roles_data import user

ENDPOINT = "/auth/v1/users/signup"
HEADERS = {"content-type": "application/json", "accept": "application/json"}


@pytest.mark.parametrize("input_data, expected_response", [correct_user])
async def test_user_correct_signup(
    db_fetchone,
    signup_user: Callable,
    input_data: dict,
    expected_response: HTTPStatus,
) -> None:
    """Регистрация пользователя с корректными данными"""

    # проверка ответа от endpoint'а
    response = await signup_user(input_data)

    assert response["body"] == expected_response

    # проверка записи в БД postgres-auth-test
    user_in_db: Record = await db_fetchone(check_user_in_db_sql)
    assert user_in_db["email"] == input_data["email"]
    assert user_in_db["username"] == input_data["username"]
    assert user_in_db["first_name"] == input_data["first_name"]
    assert user_in_db["last_name"] == input_data["last_name"]
    assert user_in_db["is_active"] is True


@pytest.mark.parametrize("input_data, expected_response", all_incorrect_users)
async def test_user_incorrect_signup(
    signup_user: Callable,
    input_data: dict,
    expected_response: HTTPStatus,
) -> None:
    """Регистрация пользователя с некорректными данными"""

    response = await signup_user(input_data)
    assert response["status"] == expected_response


async def test_user_double_signup(
    signup_user: Callable,
) -> None:
    """Регистрация пользователей с имеющимся в БД email и username"""

    # проверка регистрации с имеющимся в БД email/username
    await signup_user(user)
    response = await signup_user(user)
    assert response["status"] == HTTPStatus.BAD_REQUEST
