import json
from unittest.mock import patch, MagicMock
from typing import Iterable, cast

import pytest
from data_hub_api.docmaps.v2.api_input_typing import ApiInput

from data_hub_api.utils.cache import InMemorySingleObjectCache
from data_hub_api.docmaps.v2 import provider as provider_module
from data_hub_api.docmaps.v2.provider import (
    get_docmap_item_for_query_result_item,
    DocmapsProvider
)
from tests.unit_tests.docmaps.v2.test_data import DOCMAPS_QUERY_RESULT_ITEM_1


@pytest.fixture(name='iter_dict_from_bq_query_mock', autouse=True)
def _iter_dict_from_bq_query_mock() -> Iterable[MagicMock]:
    with patch.object(provider_module, 'iter_dict_from_bq_query') as mock:
        yield mock


def _get_docmaps_index_dict(provider: DocmapsProvider) -> dict:
    return json.loads(
        ''.join(provider.iter_docmaps_index_json_stream())
    )


class TestEnhancedPreprintsDocmapsProvider:
    def test_should_create_index_with_non_empty_docmaps(
        self,
        iter_dict_from_bq_query_mock: MagicMock
    ):
        iter_dict_from_bq_query_mock.return_value = iter([
            DOCMAPS_QUERY_RESULT_ITEM_1
        ])
        docmaps_index = _get_docmaps_index_dict(DocmapsProvider())
        assert docmaps_index['docmaps'] == [
            get_docmap_item_for_query_result_item(cast(ApiInput, DOCMAPS_QUERY_RESULT_ITEM_1))
        ]

    def test_should_cache_docmaps_query_results(
        self,
        iter_dict_from_bq_query_mock: MagicMock
    ):
        iter_dict_from_bq_query_mock.return_value = [
            DOCMAPS_QUERY_RESULT_ITEM_1
        ]
        docmaps_provider = DocmapsProvider(
            query_results_cache=InMemorySingleObjectCache(max_age_in_seconds=10)
        )
        docmaps_index = _get_docmaps_index_dict(docmaps_provider)
        docmaps_index = _get_docmaps_index_dict(docmaps_provider)
        assert iter_dict_from_bq_query_mock.call_count == 1
        assert docmaps_index['docmaps'] == [
            get_docmap_item_for_query_result_item(cast(ApiInput, DOCMAPS_QUERY_RESULT_ITEM_1))
        ]
