from http import HTTPStatus

import pytest
from aiohttp import ClientSession

pytestmark = pytest.mark.asyncio


async def test_get_templates_wo_auth(notifications_api_templates_url):
    async with ClientSession() as session:
        url = f"{notifications_api_templates_url}/"

        async with session.get(url) as response:
            assert (
                response.status == HTTPStatus.FORBIDDEN
            ), f"API response status is not {HTTPStatus.FORBIDDEN}"


async def test_get_templates(notifications_api_templates_url, access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    async with ClientSession(headers=headers) as session:
        url = f"{notifications_api_templates_url}/"

        async with session.get(url) as response:
            assert (
                response.status == HTTPStatus.OK
            ), f"API response status is not {HTTPStatus.OK}"
            body = await response.json()
            assert isinstance(body, list)
            assert len(body) >= 0


async def test_create_template_wo_auth(notifications_api_templates_url):
    async with ClientSession() as session:
        url = f"{notifications_api_templates_url}/"

        async with session.post(
            url, json={"name": "test", "content": "test"}
        ) as response:
            assert (
                response.status == HTTPStatus.FORBIDDEN
            ), f"API response status is not {HTTPStatus.FORBIDDEN}"


async def test_create_template(notifications_api_templates_url, access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    async with ClientSession(headers=headers) as session:
        url = f"{notifications_api_templates_url}/"

        async with session.post(
            url, json={"name": "test", "description": "test", "template": "test"}
        ) as response:
            assert (
                response.status == HTTPStatus.CREATED
            ), f"API response status is not {HTTPStatus.CREATED}"
            body = await response.json()
            assert isinstance(body, dict)
            assert "id" in body
