import os

import requests
import pytest


DEFAULT_DATA_HUB_API_REGRESSION_TEST_URL_PREFIX = 'http://localhost:8000'
DATA_HUB_API_REGRESSION_TEST_URL_PREFIX_ENV = 'DATA_HUB_API_REGRESSION_TEST_URL_PREFIX'

EVALUATION_BY_ID_PATH = (
    '/enhanced-preprints/docmaps/v2/evaluation/get-by-evaluation-id'
)

EVALUATION_ID_LIST = [
    'E9MOvpsrEe2w6nds1t6xxQ',
]


@pytest.fixture(name='regression_test_url_prefix')
def _regression_test_url_prefix() -> str:
    return os.getenv(
        DATA_HUB_API_REGRESSION_TEST_URL_PREFIX_ENV,
        DEFAULT_DATA_HUB_API_REGRESSION_TEST_URL_PREFIX
    )


@pytest.fixture(name='regression_test_evaluations_url')
def _regression_test_evaluations_url(
    regression_test_url_prefix: str
) -> str:
    return regression_test_url_prefix + EVALUATION_BY_ID_PATH


@pytest.mark.parametrize('evaluation_id', EVALUATION_ID_LIST)
def test_should_evaluation_match_example_response(
    regression_test_evaluations_url: str,
    evaluation_id: str
):
    response = requests.get(
        url=regression_test_evaluations_url,
        params={'evaluation_id': evaluation_id},
        timeout=120
    )
    response.raise_for_status()
    with open(
        f'data/docmaps/regression_test/evaluation_by_evaluation_id/{evaluation_id}.html',
        'r',
        encoding='utf-8'
    ) as file:
        expected_lines = [line.strip() for line in file.readlines()]

    response_lines = [line.strip() for line in response.text.split("\n")]
    assert response_lines == expected_lines
