from unittest.mock import call, patch, MagicMock
from typing import Iterable, Sequence

import pytest

from fastapi.testclient import TestClient

from data_hub_api import main as main_module
from data_hub_api.main import create_app


@pytest.fixture(name='enhanced_preprints_docmaps_provider_class_mock', autouse=True)
def _enhanced_preprints_docmaps_provider_class_mock() -> Iterable[MagicMock]:
    with patch.object(main_module, 'EnhancedPreprintsDocmapsProvider') as mock:
        yield mock


@pytest.fixture(name='docmaps_provider_mock_list')
def _docmaps_provider_mock_list(
    enhanced_preprints_docmaps_provider_class_mock: MagicMock
) -> Sequence[MagicMock]:
    mock_list = [MagicMock(name='enhanced-reviews'), MagicMock(name='public-reviews')]
    enhanced_preprints_docmaps_provider_class_mock.side_effect = mock_list
    return mock_list


@pytest.fixture(name='enhanced_preprints_docmaps_provider_mock')
def _enhanced_preprints_docmaps_provider_mock(
    docmaps_provider_mock_list: Sequence[MagicMock]
) -> MagicMock:
    return docmaps_provider_mock_list[0]


@pytest.fixture(name='public_reviews_docmaps_provider_mock')
def _public_reviews_docmaps_provider_mock(
    docmaps_provider_mock_list: Sequence[MagicMock]
) -> MagicMock:
    return docmaps_provider_mock_list[1]




def test_read_main():
    client = TestClient(create_app())
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}


class TestGetEnhancedPreprintsDocmapsIndex:
    def test_should_return_json_with_docmaps_list_from_enhanced_preprint_provider(
        self,
        enhanced_preprints_docmaps_provider_mock: MagicMock
    ):
        docmaps_index = [{'docmaps': [{'id': 'docmap_1'}, {'id': 'docmap_2'}]}]
        enhanced_preprints_docmaps_provider_mock.get_docmaps_index.return_value = docmaps_index
        client = TestClient(create_app())
        response = client.get("/enhanced-preprints/docmaps/v1/index")
        assert response.json() == docmaps_index

    def test_should_return_json_with_docmaps_list_from_public_review_provider(
        self,
        public_reviews_docmaps_provider_mock: MagicMock
    ):
        docmaps_index = [{'docmaps': [{'id': 'docmap_1'}, {'id': 'docmap_2'}]}]
        public_reviews_docmaps_provider_mock.get_docmaps_index.return_value = docmaps_index
        client = TestClient(create_app())
        response = client.get("/public-reviews/docmaps/v1/index")
        assert response.json() == docmaps_index

    def test_should_pass_correct_parameters_to_provider_class(
        self,
        enhanced_preprints_docmaps_provider_class_mock: MagicMock
    ):
        create_app()
        enhanced_preprints_docmaps_provider_class_mock.assert_has_calls(
            [
                call(
                    only_include_reviewed_preprint_type=True,
                    only_include_evaluated_preprints=False
                ),
                call(
                    only_include_reviewed_preprint_type=False,
                    only_include_evaluated_preprints=True
                )
            ],
            any_order=False
        )
