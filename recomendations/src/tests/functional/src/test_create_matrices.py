from http import HTTPStatus

import pytest
from aiohttp import ClientSession

pytestmark = pytest.mark.asyncio


async def test_create_matrices(recommendations_api_create_matrices_url):
    async with ClientSession() as session:
        url = f"{recommendations_api_create_matrices_url}"

        async with session.get(url) as response:
            assert (
                response.status == HTTPStatus.OK
            ), f"API response status is not {HTTPStatus.OK}"
