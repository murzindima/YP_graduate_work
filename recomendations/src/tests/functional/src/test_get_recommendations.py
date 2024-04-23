from http import HTTPStatus

import pytest
from aiohttp import ClientSession

pytestmark = pytest.mark.asyncio


async def test_get_recommendations(recommendations_api_get_recommendations_url):
    async with ClientSession() as session:
        url = f"{recommendations_api_get_recommendations_url}"

        async with session.get(url) as response:
            assert (
                response.status == HTTPStatus.OK
            ), f"API response status is not {HTTPStatus.OK}"
            body = await response.json()
            assert isinstance(body, list)
            assert len(body) >= 0
