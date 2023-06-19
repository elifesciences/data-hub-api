from unittest.mock import MagicMock
import pytest

from fastapi.testclient import TestClient
from fastapi import FastAPI

from data_hub_api.docmaps.v1.api_router import create_docmaps_router

PREPRINT_DOI = '10.1101/doi1'
MANUSCRIPT_ID = 'manuscript_id_1'


@pytest.fixture(name='docmaps_provider_mock')
def _docmaps_provider_mock() -> MagicMock:
    return MagicMock(name='docmaps_provider_mock')


def create_test_client(docmaps_provider_mock: MagicMock):
    app = FastAPI()
    app.include_router(create_docmaps_router(docmaps_provider_mock))
    client = TestClient(app)
    return client


class TestGetEnhancedPreprintsDocmapsIndex:
    def test_should_return_json_with_docmaps_list_from_enhanced_preprint_provider(
        self,
        docmaps_provider_mock: MagicMock
    ):
        docmaps_index = [{'docmaps': [{'id': 'docmap_1'}, {'id': 'docmap_2'}]}]
        docmaps_provider_mock.get_docmaps_index.return_value = docmaps_index
        client = create_test_client(docmaps_provider_mock)
        response = client.get('/v1/index')
        assert response.json() == docmaps_index

    def test_should_return_not_available_message_for_invalid_manuscript_id_by_elife(
        self,
        docmaps_provider_mock: MagicMock
    ):
        docmaps_provider_mock.get_docmaps_by_manuscript_id.return_value = []
        client = create_test_client(docmaps_provider_mock)
        response = client.get(
            '/v1/by-publisher/elife/get-by-manuscript-id',
            params={'manuscript_id': MANUSCRIPT_ID}
        )
        assert response.status_code == 404
        assert response.json() == {
            "detail": "No Docmaps available for requested manuscript from the publisher eLife"
        }

    def test_should_return_docmap_from_provider_by_publisher_for_individual_manuscript_id(
        self,
        docmaps_provider_mock: MagicMock
    ):
        article_docmap_list = [{'id': 'docmap_1'}]
        docmaps_provider_mock.get_docmaps_by_manuscript_id.return_value = (
            article_docmap_list
        )
        client = create_test_client(docmaps_provider_mock)
        response = client.get(
            '/v1/by-publisher/elife/get-by-manuscript-id',
            params={'manuscript_id': MANUSCRIPT_ID}
        )
        docmaps_provider_mock.get_docmaps_by_manuscript_id.assert_called_with(
            MANUSCRIPT_ID
        )
        assert response.status_code == 200
        assert response.json() == article_docmap_list[0]
