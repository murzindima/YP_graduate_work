"""Проверка удадения ролей у пользователя."""

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
    check_user_roles_in_db_sql,
    user_delete_role_answer,
    user_without_role_answer,
)


async def test_delete_user_roles_without_authorization(
    remove_user_role: Callable,
) -> None:
    """Удаляем пользователю роль без авторизации."""
    response = await remove_user_role(user_role_data=role_to_user[0])
    assert response["status"] == HTTPStatus.UNAUTHORIZED
    assert response["body"] == unauthorized


async def test_delete_user_roles_by_simple_user(
    remove_user_role: Callable,
    signup_user: Callable,
    get_authorization_headers: Callable,
) -> None:
    """Удаляем пользователю роль от имени простого пользователя."""
    await signup_user(user)
    user_headers = await get_authorization_headers(user)
    response = await remove_user_role(
        headers=user_headers, user_role_data=role_to_user[0]
    )
    assert response["status"] == HTTPStatus.FORBIDDEN
    assert response["body"] == forbidden


async def test_delete_user_roles_to_not_exist_user(
    remove_user_role: Callable, get_authorization_headers: Callable
) -> None:
    """Удаляем несуществующему пользователю роль."""
    admin_headers = await get_authorization_headers(admin)
    response = await remove_user_role(
        headers=admin_headers, user_role_data=role_to_user[0]
    )
    assert response["status"] == HTTPStatus.NOT_FOUND
    assert response["body"] == no_user


async def test_delete_not_exist_role_by_admin(
    remove_user_role: Callable,
    signup_user: Callable,
    get_authorization_headers: Callable,
) -> None:
    """Удаляем несуществующую роль от имени админа."""
    admin_headers = await get_authorization_headers(admin)
    await signup_user(user)
    response = await remove_user_role(
        headers=admin_headers, user_role_data=role_to_user[0]
    )
    assert response["status"] == HTTPStatus.NOT_FOUND
    assert response["body"] == no_roles


async def test_delete_user_roles_without_data(
    remove_user_role: Callable,
    signup_user: Callable,
    get_authorization_headers: Callable,
) -> None:
    """Удаление роли без тела запроса от имени админа."""
    admin_headers = await get_authorization_headers(admin)
    await signup_user(user)
    response = await remove_user_role(
        headers=admin_headers, user_role_data=user
    )
    assert response["status"] == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response["body"] == no_title


async def test_delete_role_when_user_roles_not_exist_by_admin(
    create_role: Callable,
    remove_user_role: Callable,
    signup_user: Callable,
    get_authorization_headers: Callable,
) -> None:
    """Удаляем неназначенную пользователю роль от имени админа."""
    admin_headers = await get_authorization_headers(admin)
    await signup_user(user)
    await create_role(headers=admin_headers, role_data=roles[0])
    response = await remove_user_role(
        headers=admin_headers, user_role_data=role_to_user[0]
    )
    assert response["status"] == HTTPStatus.NOT_FOUND
    assert response["body"] == user_without_role_answer


async def test_delete_user_roles_by_admin(
    create_role: Callable,
    create_user_role: Callable,
    db_fetch,
    remove_user_role: Callable,
    signup_user: Callable,
    get_authorization_headers: Callable,
) -> None:
    """Удаляем неназначенную пользователю роль от имени админа."""
    admin_headers = await get_authorization_headers(admin)
    await signup_user(user)
    await create_role(headers=admin_headers, role_data=roles[0])
    response = await create_user_role(
        headers=admin_headers, user_role_data=role_to_user[0]
    )
    response = await remove_user_role(
        headers=admin_headers, user_role_data=role_to_user[0]
    )
    assert response["status"] == HTTPStatus.OK
    assert response["body"] == user_delete_role_answer
    user_roles_in_db = await db_fetch(check_user_roles_in_db_sql)
    assert len(user_roles_in_db) == 1
