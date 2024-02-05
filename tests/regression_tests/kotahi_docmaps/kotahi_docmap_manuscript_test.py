import os
import pytest
import requests
import json

DEFAULT_DATA_HUB_API_REGRESSION_TEST_URL_PREFIX = 'http://localhost:8000'
DATA_HUB_API_REGRESSION_TEST_URL_PREFIX_ENV = 'DATA_HUB_API_REGRESSION_TEST_URL_PREFIX'

DOCMAP_BY_MANUSCRIPT_PATH = (
    '/kotahi/docmaps/v1/by-publisher/elife/get-by-manuscript-id'
)

MANUSCRIPT_ID_LIST = [
    '93934'  # evaluations for 2 versions of manuscript
]

NOT_AVAILABLE_DOCMAP_JSON = {
  "detail": "No Docmaps available for requested manuscript from the publisher eLife"
}


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


#  qc_complete_timestamp > '2023-10-01' for each manuscript version
def test_docmaps_should_not_be_available_for_86628(
    regression_test_docmap_by_manuscript_url: str
):
    response = requests.get(
        url=regression_test_docmap_by_manuscript_url,
        params={'manuscript_id': '86628'}
    )
    assert response.json() == NOT_AVAILABLE_DOCMAP_JSON


#  qc_complete_timestamp > '2023-10-01' for only first manuscript version
def test_docmaps_should_not_be_available_for_86764(
    regression_test_docmap_by_manuscript_url: str
):
    response = requests.get(
        url=regression_test_docmap_by_manuscript_url,
        params={'manuscript_id': '86764'}
    )
    assert response.json() == NOT_AVAILABLE_DOCMAP_JSON


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
        f'data/docmaps/regression_test/kotahi_docmap_by_manuscript_id/{manuscript_id}.json',
        'r'
    ) as file:
        example_response = json.load(file)
    assert response.json() == example_response
