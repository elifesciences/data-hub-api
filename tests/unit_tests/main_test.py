from unittest.mock import patch, MagicMock
from typing import Iterable

import pytest

from fastapi.testclient import TestClient

from data_hub_api import main as main_module
from data_hub_api.main import create_app


@pytest.fixture(name='enhanced_preprints_docmaps_provider_class_mock', autouse=True)
def _enhanced_preprints_docmaps_provider_class_mock() -> Iterable[MagicMock]:
    with patch.object(main_module, 'EnhancedPreprintsDocmapsProvider') as mock:
        yield mock


@pytest.fixture(name='enhanced_preprints_docmaps_provider_mock')
def _enhanced_preprints_docmaps_provider_mock(
    enhanced_preprints_docmaps_provider_class_mock: MagicMock
) -> MagicMock:
    return enhanced_preprints_docmaps_provider_class_mock.return_value


def test_read_main():
    client = TestClient(create_app())
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}


class TestGetEnhancedPreprintsDocmapsIndex:
    def test_should_return_json_with_docmaps_list(
        self,
        enhanced_preprints_docmaps_provider_mock: MagicMock
    ):
        docmaps_index = [{'docmaps': [{'id': 'docmap_1'}, {'id': 'docmap_2'}]}]
        enhanced_preprints_docmaps_provider_mock.get_docmaps_index.return_value = docmaps_index
        client = TestClient(create_app())
        response = client.get("/enhanced-preprints/docmaps/v1/index")
        assert response.json() == docmaps_index
