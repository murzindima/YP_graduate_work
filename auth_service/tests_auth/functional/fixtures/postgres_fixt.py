import pytest
import asyncpg
from asyncpg import Connection
from functional.settings import test_settings


@pytest.fixture(scope="session")
async def db_conn() -> Connection:
    conn = await asyncpg.connect(test_settings.postgres_dsn)
    yield conn
    await conn.close()


@pytest.fixture(autouse=True)
async def recreate_bd(db_conn: Connection):
    await db_conn.execute("TRUNCATE public.user_role CASCADE;")
    await db_conn.execute("TRUNCATE public.users CASCADE;")
    await db_conn.execute("TRUNCATE public.role CASCADE;")
    await db_conn.execute("TRUNCATE public.refresh_tokens CASCADE;")
    await db_conn.execute("TRUNCATE public.user_activity_history CASCADE;")
    await db_conn.execute("TRUNCATE public.social_account CASCADE;")

    # добавляем в БД роль админа после отчистки базы
    await db_conn.execute(
        "INSERT INTO public.role (id, title, description, created_at, "
        "modified_at) VALUES ('b96a5e2d-327d-4e10-a8ad-f3db78fd4171', 'admin', "
        "'Повелитель всего', NOW(), NOW());"
    )

    # добавляем в БД админа после отчистки базы
    await db_conn.execute(
        "INSERT INTO users (id, username, email, hashed_password, first_name, "
        "last_name, is_active, created_at, modified_at) VALUES "
        "('b96a5e2d-327d-4e10-a8ad-f3db78fd4170', 'admin', 'admin@admin.com', "
        "'$2b$12$BwkpDHSV4zPPwiYnyOJ7oeL0CPi2LET3HFQDndoe5K9xPc7jS4zuu', "
        "'first_name', 'last_name', true, NOW(), NOW());"
    )

    # добавляем в БД роль админy после отчистки базы
    await db_conn.execute(
        "INSERT INTO public.user_role (id, user_id, role_id, expire_at, "
        "is_active, created_at, modified_at) VALUES "
        "('b96a5e2d-327d-4e10-a8ad-f3db78fd4172', "
        "'b96a5e2d-327d-4e10-a8ad-f3db78fd4170', "
        "'b96a5e2d-327d-4e10-a8ad-f3db78fd4171', null, true, NOW(), NOW());"
    )


@pytest.fixture(autouse=False)
async def db_empty_social_account_table(db_conn: Connection):
    result = await db_conn.execute("TRUNCATE public.social_account CASCADE;")
    return result


@pytest.fixture(autouse=False)
async def db_empty_users_table(db_conn: Connection):
    result = await db_conn.execute("TRUNCATE public.users CASCADE;")
    return result


@pytest.fixture(autouse=False)
async def db_empty_roles_table(db_conn: Connection):
    result = await db_conn.execute("TRUNCATE public.role CASCADE;")
    return result


@pytest.fixture(autouse=False)
async def db_empty_user_role_table(db_conn: Connection):
    result = await db_conn.execute("TRUNCATE public.user_role CASCADE;")
    return result


@pytest.fixture(autouse=False)
async def db_empty_refresh_tokens_table(db_conn: Connection):
    result = await db_conn.execute("TRUNCATE public.refresh_tokens CASCADE;")
    return result


@pytest.fixture(autouse=False)
async def db_empty_user_activity_history_table(db_conn: Connection):
    result = await db_conn.execute(
        "TRUNCATE public.user_activity_history CASCADE;"
    )
    return result


@pytest.fixture
async def db_fetchone(db_conn: Connection):
    async def inner(sql):
        result = await db_conn.fetchrow(sql)
        return result

    return inner


@pytest.fixture
async def db_fetch(db_conn: Connection):
    async def inner(sql):
        result = await db_conn.fetch(sql)
        return result

    return inner


@pytest.fixture
def is_id_exists(db_conn: Connection):
    """Существует ли запись с таким id в таблице БД."""

    async def inner(table_name: str, id: str):
        sql = f"SELECT 1 FROM {table_name} WHERE id = '{id}';"
        result = await db_conn.fetch(sql)
        return result

    return inner
