import os
import json
import pytest
import requests

DEFAULT_DATA_HUB_API_REGRESSION_TEST_URL_PREFIX = 'http://localhost:8000'
DATA_HUB_API_REGRESSION_TEST_URL_PREFIX_ENV = 'DATA_HUB_API_REGRESSION_TEST_URL_PREFIX'

DOCMAP_BY_MANUSCRIPT_PATH = (
    '/kotahi/docmaps/v1/by-publisher/elife/get-by-manuscript-id'
)
EVALUATION_BY_ID_PATH = (
    '/kotahi/docmaps/v1/evaluation/get-by-evaluation-id'
)

MANUSCRIPT_ID_LIST = [
    '93934'  # evaluations for 2 versions of manuscript
]

EVALUATION_ID_LIST = [
    'eLife-RP-TR-2023-93934:evaluation-summary:1',
    'eLife-RP-TR-2023-93934:review-article:1',
    'eLife-RP-RA-2024-104041:evaluation-summary:1'
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


@pytest.fixture(name='regression_test_evaluations_url')
def _regression_test_evaluations_url(
    regression_test_url_prefix: str
) -> str:
    return regression_test_url_prefix + EVALUATION_BY_ID_PATH


def test_docmaps_should_not_be_available_for_manuscript_with_all_versions_before_cutoff_date(
    regression_test_docmap_by_manuscript_url: str
):
    response = requests.get(
        url=regression_test_docmap_by_manuscript_url,
        params={'manuscript_id': '86628'},
        timeout=120
    )
    assert response.status_code == 404


def test_docmaps_should_not_be_available_for_manuscript_with_only_first_version_before_cutoff_date(
    regression_test_docmap_by_manuscript_url: str
):
    response = requests.get(
        url=regression_test_docmap_by_manuscript_url,
        params={'manuscript_id': '86764'},
        timeout=120
    )
    assert response.status_code == 404


@pytest.mark.parametrize('manuscript_id', MANUSCRIPT_ID_LIST)
def test_should_match_example_response(
    regression_test_docmap_by_manuscript_url: str,
    manuscript_id: str
):
    response = requests.get(
        url=regression_test_docmap_by_manuscript_url,
        params={'manuscript_id': manuscript_id},
        timeout=120
    )
    response.raise_for_status()
    with open(
        f'data/docmaps/regression_test/kotahi_docmap_by_manuscript_id/{manuscript_id}.json',
        'r',
        encoding='utf-8'
    ) as file:
        example_response = json.load(file)
    assert response.json() == example_response


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
        f'data/docmaps/regression_test/kotahi_evaluation_by_evaluation_id/{evaluation_id}.txt',
        'r',
        encoding='utf-8'
    ) as file:
        expected_lines = [line.strip() for line in file.readlines()]

    response_lines = [line.strip() for line in response.text.split("\n")]
    assert response_lines == expected_lines
