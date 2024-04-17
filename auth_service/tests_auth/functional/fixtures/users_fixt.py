import uuid
from typing import Callable
import orjson
import pytest
from asyncpg import Connection

from functional.settings import test_settings
from functional.services import create_hashed_password


ENDPOINT_SIGNUP = (
    f"{test_settings.common_users}{test_settings.endpoint_sign_up}"
)


@pytest.fixture
def signup_user(make_post_request: Callable) -> Callable:
    """Регистрация пользователя."""

    async def inner(user_data: dict | None = None) -> dict:
        response = await make_post_request(
            headers=test_settings.headers_common,
            data=orjson.dumps(user_data),
            endpoint=ENDPOINT_SIGNUP,
        )
        return response

    return inner


@pytest.fixture
def get_user_from_db(db_conn: Connection) -> Callable:
    """Получить пользователя из БД."""

    async def inner(field: str, value: str) -> dict:
        sql = f"SELECT * FROM users WHERE {field} = '{value}';"
        result = await db_conn.fetchrow(sql)
        return result

    return inner


@pytest.fixture
def update_user_by_admin(make_post_request: Callable) -> Callable:
    """Измеенние пользователя админом."""

    async def inner(user_data: dict | None = None) -> dict:
        response = await make_post_request(
            headers=test_settings.headers_common,
            data=orjson.dumps(user_data),
            endpoint=ENDPOINT_SIGNUP,
        )
        return response

    return inner


@pytest.fixture
def create_user_in_db(db_conn: Connection) -> Callable:
    """Создать пользователя в БД."""

    async def inner(user_data: dict) -> None:
        id = user_data["id"]
        username = user_data["username"]
        email = user_data["email"]
        first_name = user_data["first_name"]
        last_name = user_data["last_name"]
        is_active = user_data["is_active"]
        hashed_password = create_hashed_password(user_data["password"])
        sql = (
            f"INSERT INTO users (id, username, email, hashed_password,"
            f" first_name, last_name, is_active, created_at, modified_at)"
            f" VALUES ('{id}', '{username}', '{email}', '{hashed_password}',"
            f" '{first_name}', '{last_name}', {is_active}, NOW(), NOW());"
        )
        await db_conn.execute(sql)

    return inner


@pytest.fixture
def create_user_history_in_db(db_conn: Connection) -> Callable:
    """Создать историю пользователя в БД."""

    async def inner(user_id: str, number_rows: int) -> None:
        for _ in range(number_rows):
            id = str(uuid.uuid4())
            user_agent = f"UA {user_id[-1:]}"
            sql = (
                f"INSERT INTO user_activity_history (id, user_id, user_agent,"
                f" activity, created_at, modified_at)"
                f" VALUES ('{id}', '{user_id}', '{user_agent}', 'login',"
                f" NOW(), NOW());"
            )
            await db_conn.execute(sql)

    return inner
