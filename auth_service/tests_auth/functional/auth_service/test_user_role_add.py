"""Проверка добавления ролей пользователю."""

from http import HTTPStatus
from typing import Callable

from functional.test_data.roles_data import (
    roles,
    admin,
    role_to_user,
    unauthorized,
    user,
    forbidden,
    no_roles,
    no_user,
    no_title,
    user_add_new_role_answer,
    user_add_second_role_answer,
    user_override_role_answer,
    check_user_roles_in_db_sql,
)


async def test_post_user_roles_without_authorization(
    create_user_role: Callable,
) -> None:
    """Добавляем пользователю роль без авторизации."""
    response = await create_user_role(user_role_data=role_to_user[0])
    assert response["status"] == HTTPStatus.UNAUTHORIZED
    assert response["body"] == unauthorized


async def test_post_user_roles_by_simple_user(
    create_user_role: Callable,
    signup_user: Callable,
    get_authorization_headers: Callable,
) -> None:
    """Добавляем пользователю роль от имени простого пользователя."""
    await signup_user(user)
    user_headers = await get_authorization_headers(user)
    response = await create_user_role(
        headers=user_headers, user_role_data=role_to_user[0]
    )
    assert response["status"] == HTTPStatus.FORBIDDEN
    assert response["body"] == forbidden


async def test_post_user_roles_to_not_exist_user(
    create_user_role: Callable, get_authorization_headers: Callable
) -> None:
    """Добавляем несуществующему пользователю роль."""
    admin_headers = await get_authorization_headers(admin)
    response = await create_user_role(
        headers=admin_headers, user_role_data=role_to_user[0]
    )
    assert response["status"] == HTTPStatus.NOT_FOUND
    assert response["body"] == no_user


async def test_post_user_roles_without_data(
    create_user_role: Callable,
    signup_user: Callable,
    get_authorization_headers: Callable,
) -> None:
    """Добавление роли без тела запроса от имени админа."""
    admin_headers = await get_authorization_headers(admin)
    await signup_user(user)
    response = await create_user_role(
        headers=admin_headers, user_role_data=user
    )
    assert response["status"] == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response["body"] == no_title


async def test_post_user_roles_when_role_not_exist(
    create_user_role: Callable,
    signup_user: Callable,
    get_authorization_headers: Callable,
) -> None:
    """Добавляем несуществующую роль пользователю."""
    admin_headers = await get_authorization_headers(admin)
    await signup_user(user)
    response = await create_user_role(
        headers=admin_headers, user_role_data=role_to_user[0]
    )
    assert response["status"] == HTTPStatus.NOT_FOUND
    assert response["body"] == no_roles


async def test_post_user_roles_by_admin(
    create_role: Callable,
    create_user_role: Callable,
    db_fetch,
    signup_user: Callable,
    get_authorization_headers: Callable,
) -> None:
    """Добавляем пользователю роль от имени админа."""
    admin_headers = await get_authorization_headers(admin)
    await signup_user(user)
    await create_role(headers=admin_headers, role_data=roles[0])
    response = await create_user_role(
        headers=admin_headers, user_role_data=role_to_user[0]
    )
    assert response["status"] == HTTPStatus.OK
    assert response["body"] == user_add_new_role_answer
    user_roles_in_db = await db_fetch(check_user_roles_in_db_sql)
    assert len(user_roles_in_db) == 2


async def test_post_user_roles_override_by_admin(
    create_role: Callable,
    create_user_role: Callable,
    db_fetch,
    signup_user: Callable,
    get_authorization_headers: Callable,
) -> None:
    """Дважды добавляем пользователю роль от имени админа."""
    admin_headers = await get_authorization_headers(admin)
    await signup_user(user)
    await create_role(headers=admin_headers, role_data=roles[0])
    await create_user_role(
        headers=admin_headers, user_role_data=role_to_user[0]
    )
    response = await create_user_role(
        headers=admin_headers, user_role_data=role_to_user[0]
    )
    assert response["status"] == HTTPStatus.BAD_REQUEST
    assert response["body"] == user_override_role_answer
    user_roles_in_db = await db_fetch(check_user_roles_in_db_sql)
    assert len(user_roles_in_db) == 2


async def test_post_user_second_role_by_admin(
    create_role: Callable,
    create_user_role: Callable,
    db_fetch,
    signup_user: Callable,
    get_authorization_headers: Callable,
) -> None:
    """Добавляем пользователю вторую роль от имени админа."""
    admin_headers = await get_authorization_headers(admin)
    await signup_user(user)
    await create_role(headers=admin_headers, role_data=roles[0])
    await create_role(headers=admin_headers, role_data=roles[1])
    await create_user_role(
        headers=admin_headers, user_role_data=role_to_user[0]
    )
    response = await create_user_role(
        headers=admin_headers, user_role_data=role_to_user[1]
    )
    assert response["status"] == HTTPStatus.OK
    assert response["body"] == user_add_second_role_answer
    user_roles_in_db = await db_fetch(check_user_roles_in_db_sql)
    assert len(user_roles_in_db) == 3
