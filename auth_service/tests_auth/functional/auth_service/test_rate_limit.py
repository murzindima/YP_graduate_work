from http import HTTPStatus
from typing import Callable

from orjson import orjson

from functional.settings import test_settings

REQUEST_LIMIT_PER_MIN = 20


async def test_rate_limit(
    make_post_request: Callable,
):
    endpoint = f"{test_settings.common_users}{test_settings.endpoint_sign_up}"
    for i in range(REQUEST_LIMIT_PER_MIN + 5):
        user_data = {
            "username": f"user{i}",
            "password": f"password{i}",
            "email": f"user{i}@mail.ru",
            "first_name": f"user{i}",
            "last_name": f"user{i}",
        }
        response = await make_post_request(
            endpoint=endpoint,
            data=orjson.dumps(user_data),
            headers=test_settings.headers_common,
        )
        if i < REQUEST_LIMIT_PER_MIN:
            assert response["status"] != HTTPStatus.TOO_MANY_REQUESTS
        else:
            assert response["status"] == HTTPStatus.TOO_MANY_REQUESTS
