import pytest
import requests
import json

DOCMAP_BY_MANUSCRIPT_PATH = (
    '/enhanced-preprints/docmaps/v2/by-publisher/elife/get-by-manuscript-id'
)


@pytest.fixture(name='regression_test_url_prefix')
def _regression_test_url_prefix() -> str:
    return 'http://localhost:8000'


@pytest.fixture(name='regression_test_docmap_by_manuscript_url')
def _regression_test_docmap_by_manuscript_url(
    regression_test_url_prefix: str
) -> str:
    return regression_test_url_prefix + DOCMAP_BY_MANUSCRIPT_PATH


def test_should_match_example_response_for_86628(
    regression_test_docmap_by_manuscript_url: str
):
    response = requests.get(
        url=regression_test_docmap_by_manuscript_url,
        params={'manuscript_id': '86628'}
    )
    response.raise_for_status()
    with open('data/docmaps/sample_docmap_for_86628.json', 'r') as file:
        example_response = json.load(file)
    assert response.json() == example_response
