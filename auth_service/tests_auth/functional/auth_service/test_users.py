from http import HTTPStatus
from typing import Callable


from functional.test_data.users_data import user_1, user_2


async def test_user_history(
    make_get_request: Callable,
    create_user_in_db: Callable,
    get_authorization_headers: Callable,
    create_user_history_in_db: Callable,
):
    """Проверка получения истории пользователя."""

    endpoint = "/auth/v1/users/me/history"

    # создаем пользователей
    await create_user_in_db(user_1)
    await create_user_in_db(user_2)
    user_1_headers = await get_authorization_headers(user_1)
    fields = {"user_agent", "activity", "created_at"}

    # создаем историю логинов в базе данных
    number_rows_user_1 = 15
    number_rows_user_2 = 10
    await create_user_history_in_db(user_1["id"], number_rows_user_1)
    await create_user_history_in_db(user_2["id"], number_rows_user_2)

    # делаем запрос от имени user_1
    response = await make_get_request(
        endpoint=endpoint, headers=user_1_headers
    )
    data = response["body"]

    assert response["status"] == HTTPStatus.OK
    assert len(data) == number_rows_user_1 + 1
    assert (
        sum(1 for item in data if item["user_agent"] == "UA 1")
        == number_rows_user_1
    )
    assert all(set(fields) == set(item.keys()) for item in data)
