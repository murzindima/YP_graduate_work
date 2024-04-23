import pytest

from functional.settings import test_settings

CREATE_MATRICES_SUB_PATH = "create_matrices"
USER_ID = "3c8d0006-d12b-450c-808e-4c5639f2fb4d"


@pytest.fixture
def recommendations_api_create_matrices_url():
    return f"{test_settings.recommendations_api_base_url}/{CREATE_MATRICES_SUB_PATH}"


@pytest.fixture
def recommendations_api_get_recommendations_url():
    return f"{test_settings.recommendations_api_base_url}/{USER_ID}"
