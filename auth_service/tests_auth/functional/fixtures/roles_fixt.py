from typing import Callable
import orjson
import pytest
from asyncpg import Connection

from functional.settings import test_settings


@pytest.fixture
def create_role(make_post_request: Callable) -> Callable:
    """Создать роль от имени user."""

    async def inner(
        headers: dict | None = test_settings.headers_common,
        role_data: dict | None = None,
    ) -> dict:
        response = await make_post_request(
            headers=headers,
            data=orjson.dumps(role_data),
            endpoint=test_settings.common_roles,
        )
        return response

    return inner


@pytest.fixture
async def role_in_db(db_conn: Connection):
    """Создать роль в БД"""
    id = "11111111-1111-1111-1111-111111111111"
    title = "role_1"
    description = "about role_1"
    sql = (
        f"INSERT INTO public.role (id, title, description, created_at, modified_at)"
        f" VALUES ('{id}', '{title}', '{description}', NOW(), NOW());"
    )
    await db_conn.execute(sql)
    yield db_conn
