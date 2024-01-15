import os
import pytest
import requests
import json

DEFAULT_DATA_HUB_API_REGRESSION_TEST_URL_PREFIX = 'http://localhost:8000'
DATA_HUB_API_REGRESSION_TEST_URL_PREFIX_ENV = 'DATA_HUB_API_REGRESSION_TEST_URL_PREFIX'

DOCMAP_BY_MANUSCRIPT_PATH = (
    '/enhanced-preprints/docmaps/v2/by-publisher/elife/get-by-manuscript-id'
)
MANUSCRIPT_ID_LIST = [
    '86628',  # bioRxiv preprint server
    '89891',  # medRxiv preprint server
    '86873',  # arXiv preprint server
    '87193',  # OSF preprint server
    '87198'  # Research Square preprint server
]


@pytest.fixture(name='regression_test_url_prefix')
def _regression_test_url_prefix() -> str:
    return os.getenv(
        DATA_HUB_API_REGRESSION_TEST_URL_PREFIX_ENV,
        DEFAULT_DATA_HUB_API_REGRESSION_TEST_URL_PREFIX
    )


@pytest.fixture(name='regression_test_docmap_by_manuscript_url')
def _regression_test_docmap_by_manuscript_url(
    regression_test_url_prefix: str
) -> str:
    return regression_test_url_prefix + DOCMAP_BY_MANUSCRIPT_PATH


@pytest.mark.parametrize('manuscript_id', MANUSCRIPT_ID_LIST)
def test_should_match_example_response(
    regression_test_docmap_by_manuscript_url: str,
    manuscript_id: str
):
    response = requests.get(
        url=regression_test_docmap_by_manuscript_url,
        params={'manuscript_id': manuscript_id}
    )
    response.raise_for_status()
    with open(
        f'data/docmaps/regression_test/docmap_by_manuscript_id/{manuscript_id}.json',
        'r'
    ) as file:
        example_response = json.load(file)
    assert response.json() == example_response
