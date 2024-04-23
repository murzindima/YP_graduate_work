from http import HTTPStatus

import pytest
from aiohttp import ClientSession

pytestmark = pytest.mark.asyncio


async def test_create_notification_wo_auth(notifications_api_notifications_url):
    async with ClientSession() as session:
        url = f"{notifications_api_notifications_url}/"

        async with session.post(
            url,
            json={
                "template_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "recipients": ["test"],
                "context": {},
            },
        ) as response:
            assert (
                response.status == HTTPStatus.FORBIDDEN
            ), f"API response status is not {HTTPStatus.FORBIDDEN}"


# TODO get template id
# async def test_create_notification(notifications_api_notifications_url, access_token):
#     headers = {"Authorization": f"Bearer {access_token}"}
#     async with ClientSession(headers=headers) as session:
#         url = f"{notifications_api_notifications_url}/"
#
#         async with session.post(
#             url, json={"template_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6", "recipients": ["test"], "context": {}}
#         ) as response:
#             assert (
#                 response.status == HTTPStatus.CREATED
#             ), f"API response status is not {HTTPStatus.CREATED}"
#             body = await response.json()
#             assert isinstance(body, dict)
#             assert "id" in body
#
